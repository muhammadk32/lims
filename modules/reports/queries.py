from extensions import db

"""Report query helpers."""


# ============================================================
# Previous results lookup for patient
# ============================================================
def get_previous_results(patient_id, current_order_id, test_name, limit=2):
    """Return list of (date, value) for the last N prior results of this test.

    Match is by test name (case-insensitive). Only looks at orders
    older than current_order_id. Ordered newest first.
    """
    from modules.orders.models import Order, OrderItem, OrderStatus
    from modules.tests.models import Test
    from sqlalchemy import func

    if not test_name:
        return []

    rows = (
        db.session.query(
            Order.created_at.label('date'),
            OrderItem.result_value.label('value'),
        )
        .join(Order, OrderItem.order_id == Order.id)
        .join(Test, OrderItem.test_id == Test.id)
        .filter(Order.patient_id == patient_id)
        .filter(Order.id < current_order_id)
        .filter(Order.status.in_([OrderStatus.COMPLETED, OrderStatus.APPROVED]))
        .filter(func.lower(Test.name) == func.lower(test_name))
        .filter(OrderItem.result_value.isnot(None))
        .filter(OrderItem.result_value != '')
        .order_by(Order.id.desc())
        .limit(limit)
        .all()
    )

    return [(r.date, r.value) for r in rows]


def build_previous_map(patient_id, current_order_id, limit=2):
    """Build {test_name_lower: [(date, value), ...]} for all tests in current order.

    Only includes tests that have at least one prior result.
    """
    from modules.orders.models import Order, OrderItem, OrderStatus
    from modules.tests.models import Test
    from sqlalchemy import func

    order = db.session.get(Order, current_order_id)
    if not order:
        return {}, []

    # Collect every test name used in the current order (top-level + children)
    names = set()
    for item in order.top_level_items:
        if item.test:
            names.add(item.test.name)
        for ch in item.children:
            if ch.test:
                names.add(ch.test.name)

    result_map = {}
    date_labels = []

    for name in names:
        priors = get_previous_results(patient_id, current_order_id, name, limit)
        if priors:
            result_map[name.lower()] = priors

    # Build consistent date headers: use the most common order positions
    # Take dates from any test that has 2 priors
    for name, priors in result_map.items():
        for i, (d, _) in enumerate(priors):
            while len(date_labels) <= i:
                date_labels.append(None)
            if date_labels[i] is None:
                date_labels[i] = d
        break  # only first test is enough for labels

    return result_map, date_labels


def outsourced_report(date_from, date_to, lab_id=None, status=None):
    """Return rows for the Outsourced Lab Tests report.

    Each row = one top-level OrderItem whose Test.is_outsourced == True.

    Filters:
      date_from / date_to : dates (inclusive)
      lab_id              : Laboratory.id (partner lab) or None for all
      status              : 'approved' | 'pending' | 'all' (default: all)
    """
    from modules.orders.models import Order, OrderItem, OrderStatus
    from modules.tests.models import Test
    from modules.laboratories.models import Laboratory

    q = (OrderItem.query
         .join(Order, OrderItem.order_id == Order.id)
         .join(Test, OrderItem.test_id == Test.id)
         .filter(OrderItem.parent_item_id.is_(None))
         .filter(Test.is_outsourced.is_(True))
         .filter(Order.status != OrderStatus.CANCELLED)
         .filter(db.func.date(Order.created_at) >= date_from)
         .filter(db.func.date(Order.created_at) <= date_to))

    if lab_id:
        q = q.filter(Test.laboratory_id == lab_id)

    if status == 'approved':
        q = q.filter(Order.status == OrderStatus.APPROVED)
    elif status == 'pending':
        q = q.filter(Order.status != OrderStatus.APPROVED)

    items = q.order_by(Order.created_at.desc(), Order.id.desc()).all()

    rows = []
    for it in items:
        o = it.order
        t = it.test
        rows.append({
            'order_id': o.id,
            'order_code': o.order_code,
            'created_at': o.created_at,
            'patient_name': (o.patient.full_name if o.patient else '-'),
            'test_code': t.code,
            'test_name': t.name,
            'lab_name': (t.laboratory_ref.name if getattr(t, 'laboratory_ref', None) else '-'),
            'price': it.price or 0.0,
            'max_discount_pct': t.max_discount_percent,
            'applied_discount_pct': it.applied_discount_pct or 0.0,
            'applied_discount_amt': it.applied_discount_amount or 0.0,
            'net': (it.price or 0.0) - (it.applied_discount_amount or 0.0),
            'order_status': o.status,
        })
    return rows
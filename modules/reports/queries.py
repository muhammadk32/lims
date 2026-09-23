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

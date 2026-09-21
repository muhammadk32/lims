"""
Aggregate data for dashboard charts and widgets.

IMPORTANT: All cross-module model imports are done INSIDE functions
(lazy imports). This prevents circular-import chains at startup.
"""
from datetime import datetime, timedelta, date
from sqlalchemy import func
from extensions import db


# ============================================================
# Lazy import helpers — called inside functions only
# ============================================================
def _models():
    """Import and return all models used by this module."""
    from modules.patients.models import Patient
    from modules.tests.models import Test
    from modules.orders.models import Order, OrderItem, OrderStatus
    from modules.billing.models import Payment
    return Patient, Test, Order, OrderItem, OrderStatus, Payment


def kpi_cards():
    Patient, Test, Order, OrderItem, OrderStatus, Payment = _models()

    today = date.today()
    yesterday = today - timedelta(days=1)

    def count_between(model, start_dt, end_dt, *criteria):
        q = model.query.filter(model.created_at >= start_dt, model.created_at <= end_dt)
        for c in criteria:
            q = q.filter(c)
        return q.count()

    # Patients
    patients_total = Patient.query.filter_by(is_active=True).count()
    patients_today = count_between(
        Patient,
        datetime.combine(today, datetime.min.time()),
        datetime.combine(today, datetime.max.time()),
    )
    patients_yesterday = count_between(
        Patient,
        datetime.combine(yesterday, datetime.min.time()),
        datetime.combine(yesterday, datetime.max.time()),
    )

    # Orders
    orders_total = Order.query.filter(Order.status != OrderStatus.CANCELLED).count()
    orders_today = count_between(
        Order,
        datetime.combine(today, datetime.min.time()),
        datetime.combine(today, datetime.max.time()),
        Order.status != OrderStatus.CANCELLED,
    )
    orders_yesterday = count_between(
        Order,
        datetime.combine(yesterday, datetime.min.time()),
        datetime.combine(yesterday, datetime.max.time()),
        Order.status != OrderStatus.CANCELLED,
    )

    # Revenue
    def sum_payments(start_dt, end_dt):
        return db.session.query(func.coalesce(func.sum(Payment.amount), 0.0)) \
            .filter(Payment.created_at >= start_dt, Payment.created_at <= end_dt).scalar()

    revenue_today = sum_payments(
        datetime.combine(today, datetime.min.time()),
        datetime.combine(today, datetime.max.time()),
    )
    revenue_yesterday = sum_payments(
        datetime.combine(yesterday, datetime.min.time()),
        datetime.combine(yesterday, datetime.max.time()),
    )
    revenue_total = db.session.query(func.coalesce(func.sum(Payment.amount), 0.0)).scalar()

    # Pending work
    pending_results = sum(
        1 for o in Order.query.filter(Order.status != OrderStatus.CANCELLED).all()
        if not o.all_results_done
    )
    unpaid_orders = sum(
        1 for o in Order.query.filter(Order.status != OrderStatus.CANCELLED).all()
        if o.balance_due > 0.01
    )

    def pct_change(today_val, yesterday_val):
        if yesterday_val == 0:
            return 100 if today_val > 0 else 0
        return round((today_val - yesterday_val) / yesterday_val * 100, 1)

    return {
        'patients_total': patients_total,
        'patients_today': patients_today,
        'patients_change': pct_change(patients_today, patients_yesterday),

        'orders_total': orders_total,
        'orders_today': orders_today,
        'orders_change': pct_change(orders_today, orders_yesterday),

        'revenue_today': revenue_today,
        'revenue_yesterday': revenue_yesterday,
        'revenue_change': pct_change(revenue_today, revenue_yesterday),
        'revenue_total': revenue_total,

        'pending_results': pending_results,
        'unpaid_orders': unpaid_orders,

        'active_tests': Test.query.filter_by(is_active=True).count(),
    }


def revenue_last_days(days=14):
    """Return (labels, values) for last N days."""
    _, _, _, _, _, Payment = _models()

    today = date.today()
    start = today - timedelta(days=days - 1)

    rows = (
        db.session.query(
            func.date(Payment.created_at).label('day'),
            func.coalesce(func.sum(Payment.amount), 0.0).label('total')
        )
        .filter(Payment.created_at >= datetime.combine(start, datetime.min.time()))
        .group_by(func.date(Payment.created_at))
        .all()
    )
    by_day = {str(r.day): float(r.total) for r in rows}

    labels, values = [], []
    for i in range(days):
        d = start + timedelta(days=i)
        key = d.strftime('%Y-%m-%d')
        labels.append(d.strftime('%b %d'))
        values.append(by_day.get(key, 0.0))

    return labels, values


def orders_last_days(days=14):
    _, _, Order, _, OrderStatus, _ = _models()

    today = date.today()
    start = today - timedelta(days=days - 1)

    rows = (
        db.session.query(
            func.date(Order.created_at).label('day'),
            func.count(Order.id).label('cnt')
        )
        .filter(
            Order.created_at >= datetime.combine(start, datetime.min.time()),
            Order.status != OrderStatus.CANCELLED,
        )
        .group_by(func.date(Order.created_at))
        .all()
    )
    by_day = {str(r.day): int(r.cnt) for r in rows}

    labels, values = [], []
    for i in range(days):
        d = start + timedelta(days=i)
        labels.append(d.strftime('%b %d'))
        values.append(by_day.get(d.strftime('%Y-%m-%d'), 0))

    return labels, values


def top_tests(limit=5):
    """Most ordered tests."""
    _, Test, _, OrderItem, _, _ = _models()

    rows = (
        db.session.query(
            Test.name, Test.code,
            func.count(OrderItem.id).label('cnt'),
            func.coalesce(func.sum(OrderItem.price), 0.0).label('revenue'),
        )
        .join(OrderItem, OrderItem.test_id == Test.id)
        .group_by(Test.id)
        .order_by(func.count(OrderItem.id).desc())
        .limit(limit)
        .all()
    )
    return [{'name': r.name, 'code': r.code, 'count': int(r.cnt), 'revenue': float(r.revenue)} for r in rows]


def top_patients(limit=5):
    """Patients with highest billing."""
    Patient, _, Order, _, OrderStatus, _ = _models()

    rows = (
        db.session.query(
            Patient.full_name, Patient.patient_code, Patient.id,
            func.count(Order.id).label('orders'),
            func.coalesce(func.sum(Order.total_amount), 0.0).label('billed'),
        )
        .join(Order, Order.patient_id == Patient.id)
        .filter(Order.status != OrderStatus.CANCELLED)
        .group_by(Patient.id)
        .order_by(func.sum(Order.total_amount).desc())
        .limit(limit)
        .all()
    )
    return [{
        'id': r.id, 'name': r.full_name, 'code': r.patient_code,
        'orders': int(r.orders), 'billed': float(r.billed),
    } for r in rows]


def order_status_breakdown():
    _, _, Order, _, _, _ = _models()

    rows = (
        db.session.query(Order.status, func.count(Order.id))
        .group_by(Order.status)
        .all()
    )
    return {status: int(count) for status, count in rows}


def pending_orders(limit=5):
    """Most recent orders with missing results."""
    _, _, Order, _, OrderStatus, _ = _models()

    out = []
    for o in Order.query.filter(Order.status != OrderStatus.CANCELLED).order_by(Order.id.desc()).limit(50).all():
        if not o.all_results_done:
            out.append(o)
        if len(out) >= limit:
            break
    return out
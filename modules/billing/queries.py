"""Query helpers for billing — pure data-fetching.

No HTTP, no flash, no commits.
"""
from datetime import datetime, timedelta, date

from sqlalchemy import func, or_

from extensions import db
from .models import Payment, PaymentMethod


# ============================================================
# Billing dashboard (order list + totals)
# ============================================================
def list_billing_orders(q='', filter_by='all'):
    """Return (orders, stats) for the billing dashboard."""
    from modules.orders.models import Order, OrderStatus
    from modules.patients.models import Patient

    query = Order.query   # includes cancelled orders for audit

    if q:
        like = f'%{q}%'
        query = query.join(Patient).filter(or_(
            Order.order_code.ilike(like),
            Patient.full_name.ilike(like),
            Patient.patient_code.ilike(like),
        ))

    orders = query.order_by(Order.id.desc()).all()

    if filter_by == 'unpaid':
        orders = [o for o in orders if o.payment_status == 'unpaid']
    elif filter_by == 'partial':
        orders = [o for o in orders if o.payment_status == 'partial']
    elif filter_by == 'paid':
        orders = [o for o in orders if o.payment_status == 'paid']

    return orders, compute_billing_stats()


def compute_billing_stats():
    """Dashboard totals. Cancelled orders are excluded from money."""
    from modules.orders.models import Order, OrderStatus

    today = date.today()

    active = Order.status != OrderStatus.CANCELLED

    total_orders = Order.query.filter(active).count()
    total_billed = (
        db.session.query(func.coalesce(func.sum(Order.total_amount), 0.0))
        .filter(active)
        .scalar()
    )
    # Payments: includes negative refunds automatically (they reduce sum)
    total_collected = (
        db.session.query(func.coalesce(func.sum(Payment.amount), 0.0))
        .scalar()
    )
    today_collected = (
        db.session.query(func.coalesce(func.sum(Payment.amount), 0.0))
        .filter(func.date(Payment.created_at) == today)
        .scalar()
    )

    # Outstanding = billed - collected, but only on active orders
    outstanding = max(0.0, total_billed - total_collected)

    return {
        'total_orders': total_orders,
        'total_billed': total_billed,
        'total_collected': total_collected,
        'today_collected': today_collected,
        'outstanding': outstanding,
    }
def paginate_payments(page=1, per_page=20):
    """Return a Flask-SQLAlchemy Pagination object of payments."""
    return (
        Payment.query
        .order_by(Payment.id.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )


# ============================================================
# Revenue report
# ============================================================
def resolve_period_range(period, start_str, end_str):
    """Return (start_dt, end_dt, ok).

    ok=False means the custom range was invalid (caller should flash).
    """
    today = date.today()

    if period == 'today':
        return (
            datetime.combine(today, datetime.min.time()),
            datetime.combine(today, datetime.max.time()),
            True,
        )
    if period == 'week':
        monday = today - timedelta(days=today.weekday())
        return (
            datetime.combine(monday, datetime.min.time()),
            datetime.now(),
            True,
        )
    if period == 'month':
        return datetime(today.year, today.month, 1), datetime.now(), True
    if period == 'year':
        return datetime(today.year, 1, 1), datetime.now(), True
    if period == 'custom' and start_str and end_str:
        try:
            s = datetime.strptime(start_str, '%Y-%m-%d')
            e = datetime.strptime(end_str, '%Y-%m-%d').replace(
                hour=23, minute=59, second=59
            )
            return s, e, True
        except ValueError:
            return (
                datetime.combine(today, datetime.min.time()),
                datetime.now(),
                False,
            )
    return (
        datetime.combine(today, datetime.min.time()),
        datetime.now(),
        True,
    )


def revenue_report(start_dt, end_dt):
    """Return a dict with all the numbers for the revenue template."""
    from modules.orders.models import Order, OrderStatus

    payments_in_range = (
        Payment.query
        .filter(Payment.created_at >= start_dt, Payment.created_at <= end_dt)
        .order_by(Payment.id.desc())
        .all()
    )

    total = sum(p.amount for p in payments_in_range)

    by_method = {}
    for p in payments_in_range:
        by_method.setdefault(p.method, 0.0)
        by_method[p.method] += p.amount

    by_day = {}
    for p in payments_in_range:
        key = p.created_at.strftime('%Y-%m-%d')
        by_day.setdefault(key, 0.0)
        by_day[key] += p.amount

    orders_created = (
        Order.query
        .filter(
            Order.created_at >= start_dt,
            Order.created_at <= end_dt,
            Order.status != OrderStatus.CANCELLED,
        )
        .count()
    )

    orders_billed = (
        db.session.query(func.coalesce(func.sum(Order.total_amount), 0.0))
        .filter(
            Order.created_at >= start_dt,
            Order.created_at <= end_dt,
            Order.status != OrderStatus.CANCELLED,
        )
        .scalar()
    )

    return {
        'payments': payments_in_range,
        'total': total,
        'by_method': by_method,
        'by_day': dict(sorted(by_day.items())),
        'orders_created': orders_created,
        'orders_billed': orders_billed,
    }

# ============================================================
# Range-based report query
# ============================================================
def list_billing_orders_for_range(date_from, date_to):
    """Return (orders, stats) for a date range — used by /billing/report."""
    from modules.orders.models import Order
    from sqlalchemy import func

    orders = (
        Order.query
        .filter(func.date(Order.created_at) >= date_from)
        .filter(func.date(Order.created_at) <= date_to)
        .order_by(Order.id.desc())
        .all()
    )

    total_billed = round(sum(o.final_total for o in orders if o.status != 'cancelled'), 2)
    total_collected = round(sum(o.paid_amount for o in orders), 2)
    outstanding = round(sum(o.balance_due for o in orders if o.status != 'cancelled'), 2)
    active_count = sum(1 for o in orders if o.status != 'cancelled')

    stats = {
        'total_billed': total_billed,
        'total_collected': total_collected,
        'outstanding': outstanding,
        'total_orders': active_count,
    }
    return orders, stats

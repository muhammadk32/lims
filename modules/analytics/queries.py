"""Query helpers for management reports — pure data-fetching."""
from datetime import datetime, date

from sqlalchemy import func

from extensions import db


def _parse_range(date_from, date_to):
    today = date.today()
    try:
        d_from = datetime.strptime(date_from, '%Y-%m-%d').date() if date_from else today.replace(day=1)
    except (ValueError, TypeError):
        d_from = today.replace(day=1)
    try:
        d_to = datetime.strptime(date_to, '%Y-%m-%d').date() if date_to else today
    except (ValueError, TypeError):
        d_to = today
    return d_from, d_to


def parse_range(date_from, date_to):
    return _parse_range(date_from, date_to)


# ============================================================
# 1. Doctor / Referral Performance
# ============================================================
def doctor_report(date_from, date_to):
    from modules.orders.models import Order, OrderStatus
    d_from, d_to = _parse_range(date_from, date_to)

    orders = (Order.query
        .filter(func.date(Order.created_at) >= d_from)
        .filter(func.date(Order.created_at) <= d_to)
        .filter(Order.status != OrderStatus.CANCELLED)
        .all())

    buckets = {}
    for o in orders:
        name = o.referred_by_name or (o.doctor.full_name if o.doctor else 'Walk-in')
        if name not in buckets:
            buckets[name] = {
                'name': name, 'orders': 0, 'tests': 0,
                'billed': 0.0, 'collected': 0.0,
            }
        b = buckets[name]
        b['orders'] += 1
        b['tests'] += o.item_count or 0
        b['billed'] += o.final_total or 0
        b['collected'] += o.paid_amount or 0

    rows = sorted(buckets.values(), key=lambda r: r['billed'], reverse=True)
    for r in rows:
        r['avg'] = round(r['billed'] / r['orders'], 2) if r['orders'] else 0
        r['billed'] = round(r['billed'], 2)
        r['collected'] = round(r['collected'], 2)

    totals = {
        'refs': len(rows),
        'orders': sum(r['orders'] for r in rows),
        'tests': sum(r['tests'] for r in rows),
        'billed': round(sum(r['billed'] for r in rows), 2),
        'collected': round(sum(r['collected'] for r in rows), 2),
    }
    return rows, totals


# ============================================================
# 2. Test Volume
# ============================================================
def test_volume_report(date_from, date_to):
    from modules.orders.models import Order, OrderItem, OrderStatus
    from modules.tests.models import Test, TestCategory
    d_from, d_to = _parse_range(date_from, date_to)

    rows_q = (db.session.query(
            Test.id, Test.code, Test.name,
            TestCategory.name.label('cat'),
            func.count(OrderItem.id).label('cnt'),
            func.coalesce(func.sum(OrderItem.price), 0.0).label('revenue'),
        )
        .join(OrderItem, OrderItem.test_id == Test.id)
        .outerjoin(TestCategory, Test.category_id == TestCategory.id)
        .join(Order, Order.id == OrderItem.order_id)
        .filter(func.date(Order.created_at) >= d_from)
        .filter(func.date(Order.created_at) <= d_to)
        .filter(Order.status != OrderStatus.CANCELLED)
        .filter(OrderItem.parent_item_id.is_(None))
        .group_by(Test.id)
        .order_by(func.count(OrderItem.id).desc())
        .all())

    rows = []
    for r in rows_q:
        cnt = int(r.cnt or 0)
        rev = float(r.revenue or 0)
        rows.append({
            'code': r.code, 'name': r.name,
            'category': r.cat or '-',
            'count': cnt,
            'revenue': round(rev, 2),
            'avg': round(rev / cnt, 2) if cnt else 0,
        })

    totals = {
        'unique_tests': len(rows),
        'total_count': sum(r['count'] for r in rows),
        'total_revenue': round(sum(r['revenue'] for r in rows), 2),
    }
    return rows, totals


# ============================================================
# 3. Abnormal Results
# ============================================================
def abnormal_report(date_from, date_to):
    from modules.orders.models import Order, OrderItem, OrderStatus
    from modules.results.validators import check_result
    d_from, d_to = _parse_range(date_from, date_to)

    items = (OrderItem.query
        .join(Order, Order.id == OrderItem.order_id)
        .filter(func.date(Order.created_at) >= d_from)
        .filter(func.date(Order.created_at) <= d_to)
        .filter(Order.status != OrderStatus.CANCELLED)
        .filter(OrderItem.result_value.isnot(None))
        .filter(OrderItem.result_value != '')
        .all())

    rows = []
    for it in items:
        nr = it.test.normal_range if it.test else None
        if not nr:
            continue
        try:
            flag = check_result(nr, it.result_value)
        except Exception:
            flag = 'unknown'
        if flag != 'abnormal':
            continue
        rows.append({
            'order_id': it.order_id,
            'order_code': it.order.order_code,
            'patient': it.order.patient.full_name,
            'patient_code': it.order.patient.patient_code,
            'test': it.test.name,
            'test_code': it.test.code,
            'value': it.result_value,
            'range': nr,
            'unit': it.test.unit or '',
            'date': it.order.created_at,
        })

    rows.sort(key=lambda r: r['date'] or datetime.min, reverse=True)

    totals = {
        'count': len(rows),
        'patients': len(set(r['patient_code'] for r in rows)),
    }
    return rows, totals


# ============================================================
# 4. Daily Summary
# ============================================================
def daily_report(date_from, date_to):
    from modules.orders.models import Order, OrderStatus
    d_from, d_to = _parse_range(date_from, date_to)

    orders = (Order.query
        .filter(func.date(Order.created_at) >= d_from)
        .filter(func.date(Order.created_at) <= d_to)
        .all())

    buckets = {}
    for o in orders:
        d = o.created_at.date() if o.created_at else None
        if not d:
            continue
        if d not in buckets:
            buckets[d] = {
                'date': d, 'orders': 0, 'cancelled': 0,
                'tests': 0, 'billed': 0.0, 'collected': 0.0,
                'outstanding': 0.0,
            }
        b = buckets[d]
        if o.status == OrderStatus.CANCELLED:
            b['cancelled'] += 1
        else:
            b['orders'] += 1
            b['tests'] += o.item_count or 0
            b['billed'] += o.final_total or 0
            b['outstanding'] += o.balance_due or 0
        b['collected'] += o.paid_amount or 0

    rows = sorted(buckets.values(), key=lambda r: r['date'], reverse=True)
    for r in rows:
        r['billed'] = round(r['billed'], 2)
        r['collected'] = round(r['collected'], 2)
        r['outstanding'] = round(r['outstanding'], 2)

    totals = {
        'days': len(rows),
        'orders': sum(r['orders'] for r in rows),
        'cancelled': sum(r['cancelled'] for r in rows),
        'billed': round(sum(r['billed'] for r in rows), 2),
        'collected': round(sum(r['collected'] for r in rows), 2),
        'outstanding': round(sum(r['outstanding'] for r in rows), 2),
    }
    return rows, totals


# ============================================================
# 5. Doctor Detail — patients for one referral
# ============================================================
def doctor_detail_report(referral_name, date_from, date_to):
    """Return (orders_rows, totals) for one referral within a range."""
    from modules.orders.models import Order, OrderStatus
    d_from, d_to = _parse_range(date_from, date_to)

    orders = (Order.query
        .filter(func.date(Order.created_at) >= d_from)
        .filter(func.date(Order.created_at) <= d_to)
        .filter(Order.status != OrderStatus.CANCELLED)
        .order_by(Order.id.desc())
        .all())

    # Filter by referral (match either referred_by_name OR doctor.full_name)
    matched = []
    for o in orders:
        name = o.referred_by_name or (o.doctor.full_name if o.doctor else 'Walk-in')
        if name == referral_name:
            matched.append(o)

    rows = []
    for o in matched:
        tests = ', '.join(i.test.name for i in o.top_level_items if i.test)
        rows.append({
            'order_id': o.id,
            'order_code': o.order_code,
            'date': o.created_at,
            'patient': o.patient.full_name,
            'patient_code': o.patient.patient_code,
            'phone': o.patient.phone or '-',
            'age': o.patient.compute_age() or '-',
            'gender': o.patient.gender or '-',
            'tests': tests,
            'test_count': o.item_count or 0,
            'billed': round(o.final_total or 0, 2),
            'collected': round(o.paid_amount or 0, 2),
            'due': round(o.balance_due or 0, 2),
            'status': o.status,
        })

    totals = {
        'orders': len(rows),
        'patients': len(set(r['patient_code'] for r in rows)),
        'tests': sum(r['test_count'] for r in rows),
        'billed': round(sum(r['billed'] for r in rows), 2),
        'collected': round(sum(r['collected'] for r in rows), 2),
        'due': round(sum(r['due'] for r in rows), 2),
    }
    return rows, totals


# ============================================================
# 6. Commission Report
# ============================================================
def commission_report(date_from, date_to):
    from modules.orders.models import Order, OrderStatus
    d_from, d_to = _parse_range(date_from, date_to)

    orders = (Order.query
        .filter(func.date(Order.created_at) >= d_from)
        .filter(func.date(Order.created_at) <= d_to)
        .filter(Order.status != OrderStatus.CANCELLED)
        .all())

    buckets = {}
    for o in orders:
        if not (o.commission_amount or 0):
            continue
        name = o.referred_by_name or (o.doctor.full_name if o.doctor else 'Walk-in')
        if name not in buckets:
            buckets[name] = {
                'name': name, 'orders': 0,
                'billed': 0.0, 'commission': 0.0,
                'paid': 0.0, 'outstanding': 0.0,
            }
        b = buckets[name]
        b['orders'] += 1
        b['billed'] += o.final_total or 0
        b['commission'] += o.commission_amount or 0
        if o.commission_paid:
            b['paid'] += o.commission_amount or 0
        else:
            b['outstanding'] += o.commission_amount or 0

    rows = sorted(buckets.values(), key=lambda r: r['commission'], reverse=True)
    for r in rows:
        for k in ('billed', 'commission', 'paid', 'outstanding'):
            r[k] = round(r[k], 2)

    totals = {
        'refs': len(rows),
        'orders': sum(r['orders'] for r in rows),
        'commission': round(sum(r['commission'] for r in rows), 2),
        'paid': round(sum(r['paid'] for r in rows), 2),
        'outstanding': round(sum(r['outstanding'] for r in rows), 2),
    }
    return rows, totals


# ============================================================
# 7. Commission Detail — per-order breakdown for one referral
# ============================================================
def commission_detail(referral_name, date_from, date_to):
    """Per-order commission breakdown for one referral.

    Commission = (Subtotal - Discount) x Commission % = Final Total x %
    """
    from modules.orders.models import Order, OrderStatus
    d_from, d_to = _parse_range(date_from, date_to)

    orders = (Order.query
        .filter(func.date(Order.created_at) >= d_from)
        .filter(func.date(Order.created_at) <= d_to)
        .filter(Order.status != OrderStatus.CANCELLED)
        .order_by(Order.id.desc())
        .all())

    matched = []
    for o in orders:
        name = o.referred_by_name or (o.doctor.full_name if o.doctor else 'Walk-in')
        if name == referral_name and (o.commission_amount or 0) > 0:
            matched.append(o)

    rows = []
    for o in matched:
        subtotal = round(o.subtotal or 0, 2)
        discount = round(o.discount_value or 0, 2)
        net = round(o.final_total or 0, 2)
        # Show the referral's CURRENT % (not derived from amount, since
        # the formula subtracts discount so back-calc would be misleading)
        pct = 0.0
        try:
            from modules.referrals.models import Referral as _Ref
            _name = o.referred_by_name or (o.doctor.full_name if o.doctor else None)
            if _name:
                _r = _Ref.query.filter(_Ref.name.ilike(_name)).first()
                if _r:
                    pct = float(_r.commission_percent or 0)
        except Exception:
            pass
        test_names = ', '.join(
            (i.test.name if i.test else '?')
            for i in o.top_level_items
        )
        rows.append({
            'order_id': o.id,
            'order_code': o.order_code,
            'date': o.created_at,
            'patient': o.patient.full_name,
            'patient_code': o.patient.patient_code,
            'tests_list': test_names,
            'tests': o.item_count or 0,
            'total': net,
            'subtotal': subtotal,
            'discount': discount,
            'net': net,
            'commission_pct': pct,
            'commission': round(o.commission_amount or 0, 2),
            'commission_paid': bool(o.commission_paid),
            'commission_paid_at': o.commission_paid_at,
        })

    totals = {
        'orders': len(rows),
        'subtotal': round(sum(r['subtotal'] for r in rows), 2),
        'discount': round(sum(r['discount'] for r in rows), 2),
        'net': round(sum(r['net'] for r in rows), 2),
        'commission': round(sum(r['commission'] for r in rows), 2),
        'paid': round(sum(r['commission'] for r in rows if r['commission_paid']), 2),
        'outstanding': round(sum(r['commission'] for r in rows if not r['commission_paid']), 2),
    }
    return rows, totals


# ============================================================
# 8. Due Collection — all orders with outstanding balance
# ============================================================
def due_report(date_from, date_to):
    """Return (orders_rows, totals) for orders with balance_due > 0.

    Orders fall off this list automatically once fully paid.
    """
    from modules.orders.models import Order, OrderStatus
    d_from, d_to = _parse_range(date_from, date_to)

    orders = (Order.query
        .filter(func.date(Order.created_at) >= d_from)
        .filter(func.date(Order.created_at) <= d_to)
        .filter(Order.status != OrderStatus.CANCELLED)
        .order_by(Order.id.asc())
        .all())

    rows = []
    for o in orders:
        due = round(o.balance_due or 0, 2)
        if due <= 0.01:
            continue
        days_old = 0
        try:
            if o.created_at:
                from datetime import date as _d
                days_old = (_d.today() - o.created_at.date()).days
        except Exception:
            pass
        rows.append({
            'order_id': o.id,
            'order_code': o.order_code,
            'date': o.created_at,
            'patient': o.patient.full_name,
            'patient_code': o.patient.patient_code,
            'phone': o.patient.phone or '-',
            'referral': o.referred_by_name or (o.doctor.full_name if o.doctor else '-'),
            'net': round(o.final_total or 0, 2),
            'paid': round(o.paid_amount or 0, 2),
            'due': due,
            'days_old': days_old,
        })

    rows.sort(key=lambda r: r['days_old'], reverse=True)

    totals = {
        'count': len(rows),
        'net': round(sum(r['net'] for r in rows), 2),
        'paid': round(sum(r['paid'] for r in rows), 2),
        'due': round(sum(r['due'] for r in rows), 2),
    }
    return rows, totals

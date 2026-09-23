"""Query helpers for orders — pure data-fetching.

No HTTP, no flash, no commits. Everything here can be called from
a route, a CLI command, or a test without a request context.
"""
import re
from datetime import datetime, date

from sqlalchemy import or_, func

from extensions import db
from .models import Order, OrderStatus


# ============================================================
# Code generators
# ============================================================
def generate_order_code():
    """Per-month serial: MMYY-N (e.g. 0926-1, 0926-2)."""
    now = datetime.now()
    prefix = now.strftime('%m%y')
    pattern = f'{prefix}-%'

    max_code = (
        db.session.query(func.max(Order.order_code))
        .filter(Order.order_code.like(pattern))
        .scalar()
    )

    last_serial = 0
    if max_code:
        try:
            last_serial = int(max_code.split('-', 1)[1])
        except (ValueError, IndexError):
            last_serial = 0

    next_serial = last_serial + 1
    while Order.query.filter_by(order_code=f'{prefix}-{next_serial}').first():
        next_serial += 1

    return f'{prefix}-{next_serial}'


def generate_patient_code():
    """Sequential 6-char patient code: P00001, P00002, ..."""
    from modules.patients.models import Patient

    pattern = re.compile(r'^P(\d{1,5})$')
    rows = (
        db.session.query(Patient.patient_code)
        .filter(Patient.patient_code.like('P%'))
        .all()
    )

    highest = 0
    for (code,) in rows:
        if not code:
            continue
        m = pattern.match(code)
        if m:
            try:
                n = int(m.group(1))
                if n > highest:
                    highest = n
            except ValueError:
                pass

    next_num = highest + 1
    code = f'P{next_num:05d}'
    while Patient.query.filter_by(patient_code=code).first():
        next_num += 1
        code = f'P{next_num:05d}'

    return code


# ============================================================
# Daily ledger
# ============================================================
def get_ledger_orders(q='', status='', paid_filter='',
                     date_from=None, date_to=None):
    """Return (orders, stats) for the ledger view.

    Filters:
      q            — free-text search (order code, patient name/code/phone)
      status       — one of OrderStatus.CHOICES
      paid_filter  — '', 'yes', 'no', 'partial'
      date_from    — date
      date_to      — date
    """
    from modules.patients.models import Patient

    query = Order.query.filter(
        func.date(Order.created_at) >= date_from,
        func.date(Order.created_at) <= date_to,
    )

    if q:
        like = f'%{q}%'
        query = query.join(Patient).filter(or_(
            Order.order_code.ilike(like),
            Patient.full_name.ilike(like),
            Patient.patient_code.ilike(like),
            Patient.phone.ilike(like),
        ))

    if status in OrderStatus.CHOICES:
        query = query.filter(Order.status == status)

    orders = query.order_by(Order.id.desc()).all()

    if paid_filter == 'yes':
        orders = [o for o in orders if o.payment_status == 'paid']
    elif paid_filter == 'no':
        orders = [o for o in orders if o.payment_status == 'unpaid']
    elif paid_filter == 'partial':
        orders = [o for o in orders if o.payment_status == 'partial']

    return orders, compute_ledger_stats(orders)


def compute_ledger_stats(orders):
    """Aggregate totals for the ledger footer.

    Cancelled orders are excluded from the money totals but counted
    separately so the operator can see them.
    """
    from .models import OrderStatus
    billable = [o for o in orders if o.status != OrderStatus.CANCELLED]
    cancelled = [o for o in orders if o.status == OrderStatus.CANCELLED]

    return {
        'total_amount':    round_money(sum(o.subtotal for o in billable)),
        'total_discount':  round_money(sum(o.discount_value for o in billable)),
        'net_amount':      round_money(sum(o.final_total for o in billable)),
        'paid_amount':     round_money(sum(o.paid_amount for o in billable)),
        'due_amount':      round_money(sum(o.balance_due for o in billable)),
        'refunded_amount': round_money(sum(o.paid_amount for o in cancelled)),
        'case_count':      len(billable),
        'cancelled_count': len(cancelled),
    }
def lookup_patients(phone='', query='', limit=10):
    """Search patients by phone or free text. Returns a list of dicts."""
    from modules.patients.models import Patient

    if not phone and not query:
        return []

    pat_q = Patient.query.filter(Patient.is_active == True)  # noqa: E712

    if phone:
        pat_q = pat_q.filter(Patient.phone.ilike(f'%{phone}%'))

    if query:
        like = f'%{query}%'
        pat_q = pat_q.filter(or_(
            Patient.full_name.ilike(like),
            Patient.patient_code.ilike(like),
            Patient.phone.ilike(like),
        ))

    results = pat_q.order_by(Patient.id.desc()).limit(limit).all()

    return [
        {
            'id': p.id,
            'patient_code': p.patient_code,
            'full_name': p.full_name,
            'age': p.compute_age(),
            'gender': p.gender,
            'phone': p.phone,
            'email': p.email,
            'address': p.address,
            'blood_group': p.blood_group,
        }
        for p in results
    ]


def search_tests(q, limit=15):
    """Return a list of test dicts (including panel children info)."""
    from modules.tests.models import Test

    if not q or len(q) < 2:
        return []

    like = f'%{q}%'
    tests = (
        Test.query
        .filter(
            Test.is_active == True,  # noqa: E712
            or_(Test.name.ilike(like), Test.code.ilike(like)),
        )
        .order_by(Test.is_panel.desc(), Test.name.asc())
        .limit(limit)
        .all()
    )

    out = []
    for t in tests:
        row = {
            'id': t.id,
            'code': t.code,
            'name': t.name,
            'price': t.price,
            'unit': t.unit,
            'normal_range': t.normal_range,
            'is_panel': t.is_panel,
            'category': t.category_ref.name if t.category_ref else None,
            'format': t.result_format,
        }
        if t.is_panel:
            params = t.get_parameters()
            row['parameter_count'] = len(params)
            row['parameters'] = [p.name for p in params]
        out.append(row)
    return out


def get_doctors():
    """Return list of active doctor dicts."""
    from core.models import User

    doctors = (
        User.query
        .filter(User.role == 'doctor', User.is_active_flag == True)  # noqa: E712
        .order_by(User.full_name.asc())
        .all()
    )
    return [
        {'id': u.id, 'name': u.full_name, 'username': u.username}
        for u in doctors
    ]


def test_price_map():
    """Return {test_id_str: price} for all active tests."""
    from modules.tests.models import Test

    tests = Test.query.filter_by(is_active=True).all()
    return {str(t.id): t.price for t in tests}


# ============================================================
# Small utilities (kept here so they're importable anywhere)
# ============================================================
def parse_date(value):
    """YYYY-MM-DD string → date, or None."""
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None


def round_money(n):
    """Round to nearest whole number, as float. Never raises."""
    try:
        return float(round(float(n or 0)))
    except (ValueError, TypeError):
        return 0.0
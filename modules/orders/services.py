"""Business logic for order creation, payment, status, approval.

No HTTP, no flash, no redirect. Pure domain operations.
"""
from datetime import datetime

from extensions import db
from core.audit import log_action
from .models import Order, OrderItem, OrderStatus
from .queries import (
    generate_order_code,
    generate_patient_code,
    parse_date,
    round_money,
)


# ============================================================
# New order (the big POST)
# ============================================================
def create_patient(form):
    """Build + persist a new Patient from the reception form.

    Returns the Patient instance (already flushed, has .id).
    Raises ValueError with a user-facing message on validation failure.
    """
    from modules.patients.models import Patient

    full_name = (
        form.get('patient_name')
        or form.get('full_name')
        or ''
    ).strip()
    if not full_name:
        raise ValueError('Patient name is required.')

    age_val = form.get('age', type=float)
    if not age_val:
        v = form.get('age_value', type=float) or 0
        unit = (form.get('age_unit') or 'years').strip()
        if not v:
            years = form.get('age_years', type=int) or 0
            months = form.get('age_months', type=int) or 0
            days = form.get('age_days', type=int) or 0
            if years or months or days:
                age_val = years + round((months * 30 + days) / 365.0, 2)
        else:
            if unit == 'years':
                age_val = v
            elif unit == 'months':
                age_val = v / 12.0
            elif unit == 'days':
                age_val = v / 365.0

    patient = Patient(
        patient_code=generate_patient_code(),
        full_name=full_name,
        age=int(round(age_val)) if age_val else None,
        date_of_birth=parse_date(form.get('date_of_birth')),
        gender=(form.get('gender') or form.get('patient_gender') or '').strip() or None,
        phone=(form.get('phone') or form.get('patient_phone') or '').strip() or None,
        email=(form.get('email') or form.get('patient_email') or '').strip() or None,
        address=(form.get('address') or form.get('patient_address') or '').strip() or None,
        blood_group=(form.get('blood_group') or form.get('patient_blood_group') or '').strip() or None,
        notes=None,
    )
    db.session.add(patient)
    db.session.flush()
    log_action(
        'create', 'patient', patient.id,
        f'Created patient {patient.full_name} ({patient.patient_code}) via reception',
    )
    return patient


def create_order(patient, tests, form, user):
    """Build + persist an Order with items, discount, and optional payment.

    Returns the Order instance (committed).
    Raises ValueError with a user-facing message on validation failure.
    """
    from modules.billing.models import Payment, PaymentMethod

    if not tests:
        raise ValueError('Please select at least one test.')

    # ---------- Referral ----------
    referred_by = (form.get('referred_by') or '').strip() or None
    doctor_id = None
    if referred_by:
        try:
            doctor_id = int(referred_by)
        except (ValueError, TypeError):
            doctor_id = None

    # ---------- Sample date ----------
    sample_date_str = form.get('sample_date') or ''
    sample_collected_at = None
    if sample_date_str:
        try:
            sample_collected_at = datetime.strptime(
                sample_date_str.replace('T', ' ')[:16], '%Y-%m-%d %H:%M'
            )
        except (ValueError, TypeError):
            sample_collected_at = None
    if not sample_collected_at:
        sample_collected_at = datetime.utcnow()

    # ---------- Create order ----------
    order = Order(
        order_code=generate_order_code(),
        patient_id=patient.id,
        doctor_id=doctor_id or user.id,
        status=OrderStatus.PENDING,
        sample_collected_at=sample_collected_at,
        notes=(form.get('notes') or '').strip() or None,
    )

    if referred_by and doctor_id is None:
        ext_note = f'Referred by: {referred_by}'
        order.notes = (order.notes + '\n' + ext_note) if order.notes else ext_note

    db.session.add(order)
    db.session.flush()

    # ---------- Items ----------
    for t in tests:
        if t.is_panel:
            parent = OrderItem(
                order_id=order.id,
                test_id=t.id,
                price=t.price,
                parent_item_id=None,
                sort_order=0,
            )
            db.session.add(parent)
            db.session.flush()
            for idx, param in enumerate(t.get_parameters()):
                db.session.add(OrderItem(
                    order_id=order.id,
                    test_id=param.id,
                    price=0.0,
                    parent_item_id=parent.id,
                    sort_order=idx,
                ))
        else:
            db.session.add(OrderItem(
                order_id=order.id,
                test_id=t.id,
                price=t.price,
                parent_item_id=None,
                sort_order=0,
            ))

    db.session.flush()

    # ---------- Discount ----------
    discount_type = (form.get('discount_type') or 'amount').strip()
    if discount_type not in ('amount', 'percent'):
        discount_type = 'amount'

    order.discount_type = discount_type
    order.discount_reason = (form.get('discount_reason') or '').strip() or None

    if discount_type == 'percent':
        try:
            pct = max(0.0, min(100.0, float(form.get('discount_percent') or 0)))
        except (ValueError, TypeError):
            pct = 0.0
        order.discount_percent = pct
        order.discount_amount = 0.0
    else:
        try:
            amt = max(0.0, float(form.get('discount_amount') or 0))
        except (ValueError, TypeError):
            amt = 0.0
        order.discount_amount = round_money(amt)
        order.discount_percent = 0.0

    order.recompute_total()

    # ---------- Payment ----------
    try:
        pay_amount = float(form.get('payment_amount') or 0)
    except (ValueError, TypeError):
        pay_amount = 0.0
    pay_amount = round_money(pay_amount)

    if pay_amount > 0.001:
        method = (form.get('payment_method') or PaymentMethod.CASH).strip()
        if method not in PaymentMethod.CHOICES:
            method = PaymentMethod.CASH

        pay_amount = min(pay_amount, order.final_total)
        db.session.add(Payment(
            order_id=order.id,
            amount=pay_amount,
            method=method,
            reference=(form.get('payment_reference') or '').strip() or None,
            notes=None,
            received_by_id=user.id,
        ))
        db.session.flush()
        order.paid = order.is_fully_paid

    db.session.commit()

    log_action(
        'create', 'order', order.id,
        f'Created order {order.order_code} for {patient.full_name} — '
        f'subtotal {order.subtotal:.2f}, discount {order.discount_value:.2f}, '
        f'total {order.final_total:.2f}',
    )
    return order


# ============================================================
# Status / payment / cancel
# ============================================================
def change_order_status(order, new_status, user):
    """Update status. Returns True on success, False if invalid."""
    if new_status not in OrderStatus.CHOICES:
        return False
    order.status = new_status
    if new_status == OrderStatus.COLLECTED and not order.sample_collected_at:
        order.sample_collected_at = datetime.utcnow()
    db.session.commit()
    log_action('status', 'order', order.id,
               f'Order {order.order_code} → {new_status}')
    return True


def set_paid(order, value, user):
    """Toggle the legacy paid flag."""
    order.paid = bool(value)
    db.session.commit()
    if value:
        log_action('payment', 'order', order.id,
                   f'Marked {order.order_code} paid (legacy flag)')
    return order


def cancel_order(order, user):
    order.status = OrderStatus.CANCELLED
    db.session.commit()
    log_action('delete', 'order', order.id,
               f'Cancelled order {order.order_code}')
    return order


# ============================================================
# Pathologist approval / correction
# ============================================================
def can_approve(user):
    return bool(user and user.is_authenticated and user.role in ('admin', 'doctor'))


def approve_order(order, user):
    """Approve a completed/correction order. Returns (ok, error_message)."""
    if order.status not in (OrderStatus.COMPLETED, OrderStatus.CORRECTION):
        return False, 'Only completed or correction orders can be approved.'
    if not order.all_results_done:
        return False, 'Cannot approve — some results are still missing.'

    order.status = OrderStatus.APPROVED
    order.reported_at = datetime.utcnow()
    order.reported_by_id = user.id
    order.correction_note = None
    db.session.commit()

    log_action('approve', 'order', order.id,
               f'Approved report {order.order_code}')
    return True, None


def send_back_order(order, reason, user):
    """Send a completed/approved order back for correction.
    Returns (ok, error_message)."""
    if order.status not in (OrderStatus.COMPLETED, OrderStatus.APPROVED):
        return False, 'Only completed or approved orders can be sent back.'
    if not reason:
        return False, 'Please provide a reason for sending back.'

    order.status = OrderStatus.CORRECTION
    order.correction_note = reason
    order.correction_at = datetime.utcnow()
    order.correction_by_id = user.id
    order.reported_at = None
    order.reported_by_id = None
    db.session.commit()

    log_action('correction', 'order', order.id,
               f'Sent back {order.order_code} for correction: {reason[:80]}')
    return True, None
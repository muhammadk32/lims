"""Business logic for order creation, payment, status, approval.

No HTTP, no flash, no redirect. Pure domain operations.
"""
from datetime import datetime

from extensions import db
from core.audit import log_action
from modules.referrals.services import upsert_referral
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
    # The form field can hold either:
    #   - a numeric User id (registered doctor)
    #   - a free-text name (external / walk-in referral)
    referred_by = (form.get('referred_by') or '').strip() or None
    doctor_id = None
    referred_by_name = None
    if referred_by:
        try:
            doctor_id = int(referred_by)
        except (ValueError, TypeError):
            referred_by_name = referred_by

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
        referred_by_name=referred_by_name,
    )

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

    # Guard: flag when 100 percent discount wipes the entire total
    _warn_full_discount = (order.subtotal > 0 and order.final_total <= 0.01)


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

    # ---------- Commission (percent of final total) ----------
    if referred_by_name:
        try:
            from modules.referrals.models import Referral as _Ref
            _ref = _Ref.query.filter(_Ref.name.ilike(referred_by_name)).first()
            if _ref and (_ref.commission_percent or 0) > 0:
                # Commission = (Subtotal x %) - Discount   (floor at 0)
                _pct = _ref.commission_percent or 0
                _sub = order.subtotal or 0
                _disc = order.discount_value or 0
                _amt = (_sub * (_pct / 100.0)) - _disc
                order.commission_amount = round(max(0.0, _amt), 2)
        except Exception as _e:
            print(f'[orders.services] commission calc failed: {_e}')

    # ---------- Referral suggestion cache ----------
    # Store the free-text name in the suggestions table for the typeahead.
    if referred_by_name:
        try:
            upsert_referral(referred_by_name)
        except Exception as e:
            print(f'[orders.services] referral upsert failed: {e}')

    db.session.commit()

    log_action(
        'create', 'order', order.id,
        f'Created order {order.order_code} for {patient.full_name} â€” '
        f'subtotal {order.subtotal:.2f}, discount {order.discount_value:.2f}, '
        f'total {order.final_total:.2f}',
    )
    # Flash a warning if the discount wiped the full amount
    if _warn_full_discount:
        try:
            from flask import flash
            flash(
                'Note: order ' + order.order_code +
                ' has a 100 percent discount - Rs 0 is due from the patient.',
                'warning',
            )
        except Exception:
            pass

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
               f'Order {order.order_code} â†’ {new_status}')
    return True


def set_paid(order, value, user):
    """Toggle the legacy paid flag."""
    order.paid = bool(value)
    db.session.commit()
    if value:
        log_action('payment', 'order', order.id,
                   f'Marked {order.order_code} paid (legacy flag)')
    return order


def cancel_order(order, reason, user):
    """Cancel an order and automatically refund any amount already paid.

    Creates a negative Payment row so the refund is deducted from the
    Cash Summary on the date of cancellation.

    Returns (ok, error_message, refund_amount).
    """
    from modules.billing.models import Payment, PaymentMethod
    from modules.orders.models import OrderStatus

    if order.status == OrderStatus.CANCELLED:
        return False, 'Order is already cancelled.', 0.0

    reason = (reason or '').strip()
    if not reason:
        return False, 'Please provide a reason for cancellation.', 0.0

    now = datetime.utcnow()
    refund_amount = round_money(order.paid_amount or 0)

    # 1. Cancel the order
    order.status = OrderStatus.CANCELLED
    order.cancel_reason = reason
    order.cancelled_at = now
    order.cancelled_by_id = user.id if user else None

    # 2. Auto-refund whatever was paid
    if refund_amount > 0.001:
        db.session.add(Payment(
            order_id=order.id,
            amount=-refund_amount,               # negative = refund
            method=PaymentMethod.CASH,
            reference='Auto-refund on cancellation',
            notes=f'Cancelled: {reason[:120]}',
            received_by_id=user.id if user else None,
        ))
        order.refunded_at = now

    db.session.commit()

    log_action(
        'cancel', 'order', order.id,
        f'Cancelled order {order.order_code} — refunded Rs {refund_amount:.2f} '
        f'({reason[:80]})',
    )
    return True, None, refund_amount


def approve_order(order, user):
    """Approve a completed/correction order. Returns (ok, error_message)."""
    if order.status not in (OrderStatus.COMPLETED, OrderStatus.CORRECTION):
        return False, 'Only completed or correction orders can be approved.'
    if not order.all_results_done:
        return False, 'Cannot approve â€” some results are still missing.'

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

# ============================================================
# Edit / unlock / un-cancel
# ============================================================
def update_order(order, form, new_test_ids, user):
    """Update an order's patient info, tests, discount and referral.

    Blocks when results exist unless the order has been unlocked by admin.
    Removing a test is blocked when that test already has a result.

    Returns (ok, error_message).
    """
    from modules.orders.models import OrderStatus, OrderItem
    from modules.patients.models import Patient
    from modules.tests.models import Test

    if order.status == OrderStatus.CANCELLED:
        return False, 'Cancelled orders cannot be edited.'
    if order.has_any_results and not order.edit_unlocked:
        return False, 'Results already entered. An admin must unlock the order first.'

    # ---- 1. Update patient ----
    patient = order.patient
    if patient:
        name = (form.get('patient_name') or '').strip()
        if name:
            patient.full_name = name
        for field in ('phone', 'email', 'address', 'gender', 'blood_group'):
            v = (form.get(f'patient_{field}') or form.get(field) or '').strip()
            if v or v == '':
                setattr(patient, field, v or None)
        try:
            age = form.get('patient_age', type=int)
            if age is not None:
                patient.age = age or None
        except Exception:
            pass

    # ---- 2. Update items ----
    current_top = list(order.top_level_items)
    incoming = set(new_test_ids or [])

    # Remove top-level items whose id is not in incoming
    for item in current_top:
        if item.id not in incoming:
            # block if it has a result (or any child has a result)
            has_result = bool((item.result_value or '').strip())
            if not has_result and item.has_children:
                has_result = any((c.result_value or '').strip() for c in item.children)
            if has_result:
                return False, f'Cannot remove "{item.test.name if item.test else item.id}" — it already has a result.'
            db.session.delete(item)

    db.session.flush()

    # Add new tests that weren't already there
    existing_test_ids = {i.test_id for i in current_top if i.id in incoming}
    for tid in new_test_ids or []:
        if tid in existing_test_ids:
            continue
        t = Test.query.get(tid)
        if not t:
            continue
        if t.is_panel:
            parent = OrderItem(order_id=order.id, test_id=t.id, price=t.price,
                               parent_item_id=None, sort_order=0)
            db.session.add(parent)
            db.session.flush()
            for idx, param in enumerate(t.get_parameters()):
                db.session.add(OrderItem(order_id=order.id, test_id=param.id, price=0.0,
                                         parent_item_id=parent.id, sort_order=idx))
        else:
            db.session.add(OrderItem(order_id=order.id, test_id=t.id, price=t.price,
                                     parent_item_id=None, sort_order=0))
    db.session.flush()

    # ---- 3. Discount ----
    dtype = (form.get('discount_type') or 'amount').strip()
    if dtype not in ('amount', 'percent'):
        dtype = 'amount'
    order.discount_type = dtype
    order.discount_reason = (form.get('discount_reason') or '').strip() or None
    if dtype == 'percent':
        try:
            order.discount_percent = max(0.0, min(100.0, float(form.get('discount_percent') or 0)))
            order.discount_amount = 0.0
        except (ValueError, TypeError):
            order.discount_percent = 0.0
    else:
        try:
            order.discount_amount = round_money(float(form.get('discount_amount') or 0))
            order.discount_percent = 0.0
        except (ValueError, TypeError):
            order.discount_amount = 0.0

    order.recompute_total()

    # ---- 4. Referral ----
    ref_name = (form.get('referred_by') or '').strip() or None
    if ref_name is not None:
        try:
            int(ref_name)
            order.referred_by_name = None
        except (ValueError, TypeError):
            order.referred_by_name = ref_name
            try:
                upsert_referral(ref_name)
            except Exception:
                pass

    # ---- 5. Lock again if admin had unlocked and no results now exist ----
    if order.edit_unlocked and not order.has_any_results:
        order.edit_unlocked = False
        order.edit_unlocked_at = None
        order.edit_unlocked_by_id = None

    db.session.commit()
    log_action('update', 'order', order.id,
               f'Edited order {order.order_code}')
    return True, None


def unlock_order(order, user):
    """Admin unlocks editing of an order with existing results."""
    if not order.has_any_results:
        return False, 'No results exist — order is already editable.'
    order.edit_unlocked = True
    order.edit_unlocked_at = datetime.utcnow()
    order.edit_unlocked_by_id = user.id
    db.session.commit()
    log_action('unlock', 'order', order.id,
               f'Unlocked {order.order_code} for editing (results exist)')
    return True, None


def lock_order(order, user):
    order.edit_unlocked = False
    order.edit_unlocked_at = None
    order.edit_unlocked_by_id = None
    db.session.commit()
    log_action('lock', 'order', order.id,
               f'Locked {order.order_code} again')
    return True, None


def un_cancel_order(order, user):
    """Admin reverses a cancellation and reverses the refund if any was made.

    Reverses the auto-refund by creating a compensating positive Payment.
    Returns (ok, error_message, restored_amount).
    """
    from modules.orders.models import OrderStatus
    from modules.billing.models import Payment, PaymentMethod

    if order.status != OrderStatus.CANCELLED:
        return False, 'Order is not cancelled.', 0.0

    # Find the auto-refund payment (if any) — negative amount
    refund_payments = [p for p in order.payments if (p.amount or 0) < -0.001]
    refund_total = sum(abs(p.amount) for p in refund_payments)

    now = datetime.utcnow()

    if refund_total > 0.001:
        # Compensating positive payment to reverse the refund
        db.session.add(Payment(
            order_id=order.id,
            amount=refund_total,
            method=PaymentMethod.CASH,
            reference='Reversal of refund (un-cancel)',
            notes=f'Reversing refund due to un-cancel by {user.username if user else "admin"}',
            received_by_id=user.id if user else None,
        ))

    order.status = OrderStatus.COMPLETED
    order.cancel_reason = None
    order.cancelled_at = None
    order.cancelled_by_id = None
    order.refunded_at = None

    db.session.commit()
    log_action('un_cancel', 'order', order.id,
               f'Un-cancelled {order.order_code} — reversed refund {refund_total:.2f}')
    return True, None, refund_total


def recalculate_commissions(date_from=None, date_to=None):
    """Recalculate commission for existing orders.

    Uses each order's current referred_by_name and the referral's CURRENT
    commission %. Returns (updated_count, total_amount).

    If date range given, only touches orders in that range.
    """
    from modules.orders.models import Order, OrderStatus
    from modules.referrals.models import Referral
    from sqlalchemy import func as _f

    query = Order.query.filter(Order.status != OrderStatus.CANCELLED)
    if date_from:
        query = query.filter(_f.date(Order.created_at) >= date_from)
    if date_to:
        query = query.filter(_f.date(Order.created_at) <= date_to)

    orders = query.all()

    # Cache referral pcts
    pcts = {r.name.lower(): (r.commission_percent or 0) for r in Referral.query.all()}

    updated = 0
    total = 0.0
    for o in orders:
        if not o.referred_by_name:
            continue
        pct = pcts.get(o.referred_by_name.lower())
        if not pct:
            continue
        _sub = o.subtotal or 0
        _disc = o.discount_value or 0
        new_amount = round(max(0.0, (_sub * (pct / 100.0)) - _disc), 2)
        if abs((o.commission_amount or 0) - new_amount) > 0.001:
            o.commission_amount = new_amount
            updated += 1
            total += new_amount

    db.session.commit()
    log_action('recalc', 'order', 0,
               f'Recalculated commission for {updated} orders — total {total:.2f}')
    return updated, round(total, 2)

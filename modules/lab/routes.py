"""
Laboratory workflow routes.

The verify queue groups pending items by their parent order, so the
pathologist sees one row per order (expandable) instead of one row
per test.
"""
from datetime import datetime, date, timedelta
from flask import (
    render_template, redirect, url_for, flash, request
)
from flask_login import login_required, current_user

from extensions import db
from core.decorators import permission_required
from core.audit import log_action
from . import lab_bp


# ============================================================
# Permission helper
# ============================================================
def _can_verify():
    """Only admin and doctor (pathologist) may verify/approve."""
    return current_user.is_authenticated and current_user.role in ('admin', 'doctor')


# ============================================================
# VERIFY QUEUE — pathologist worklist (grouped by order)
# ============================================================
@lab_bp.route('/verify')
@login_required
@permission_required('view_reports')
def verify_queue():
    """List orders with pending items awaiting pathologist verification.

    Shows ONE row per order. Expanding it reveals the individual
    top-level tests that have results but are not yet verified.

    Query params:
      ?q=...          search by Lab #, patient name/code
      ?date_from=...  YYYY-MM-DD  (defaults to 7 days ago)
      ?date_to=...    YYYY-MM-DD  (defaults to today)
    """
    from sqlalchemy import or_
    from modules.orders.models import Order, OrderItem, OrderStatus
    from modules.patients.models import Patient

    if not _can_verify():
        flash('Only a pathologist or admin can access the verification queue.',
              'danger')
        return redirect(url_for('dashboard.index'))

    q = request.args.get('q', '').strip()

    today = date.today()
    default_from = today - timedelta(days=7)

    date_from_str = request.args.get('date_from', '').strip()
    date_to_str = request.args.get('date_to', '').strip()

    if not date_from_str:
        date_from_str = default_from.strftime('%Y-%m-%d')
    if not date_to_str:
        date_to_str = today.strftime('%Y-%m-%d')

    try:
        date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        date_from = default_from
        date_from_str = default_from.strftime('%Y-%m-%d')

    try:
        date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        date_to = today
        date_to_str = today.strftime('%Y-%m-%d')

    # --- Base query: top-level items in non-cancelled orders ---
    query = (
        OrderItem.query
        .join(Order, OrderItem.order_id == Order.id)
        .filter(OrderItem.parent_item_id.is_(None))
        .filter(Order.status != OrderStatus.CANCELLED)
        .filter(db.func.date(Order.created_at) >= date_from)
        .filter(db.func.date(Order.created_at) <= date_to)
    )

    if q:
        like = f'%{q}%'
        query = (
            query
            .join(Patient, Order.patient_id == Patient.id)
            .filter(or_(
                Order.order_code.ilike(like),
                Patient.full_name.ilike(like),
                Patient.patient_code.ilike(like),
            ))
        )

    candidates = query.order_by(OrderItem.id.desc()).all()

    # --- Keep only items that are verifiable and not yet verified ---
    items = [i for i in candidates if i.is_verifiable and not i.is_verified]

    # --- Group items by their parent order (preserve newest-first order) ---
    seen_order_ids = set()
    orders = []
    for item in items:
        o = item.order
        if o.id not in seen_order_ids:
            seen_order_ids.add(o.id)
            orders.append(o)

    return render_template(
        'lab/verify.html',
        items=items,
        orders=orders,
        q=q,
        date_from=date_from_str,
        date_to=date_to_str,
        today=today.strftime('%Y-%m-%d'),
    )


# ============================================================
# VERIFY ITEMS (bulk)
# ============================================================
@lab_bp.route('/verify/bulk-approve', methods=['POST'])
@login_required
def bulk_approve():
    """Verify one or more top-level items.

    Expects form field: item_ids (multiple values).
    Skips items that aren't verifiable or already verified.
    """
    from modules.orders.models import OrderItem, Order, OrderStatus

    if not _can_verify():
        flash('Only a pathologist or admin can approve reports.', 'danger')
        return redirect(url_for('dashboard.index'))

    item_ids = request.form.getlist('item_ids', type=int)
    if not item_ids:
        flash('No items selected.', 'warning')
        return redirect(url_for('lab.verify_queue'))

    verified = []
    skipped = []
    touched_orders = set()

    for item_id in item_ids:
        item = OrderItem.query.get(item_id)
        if not item or item.is_child:
            skipped.append(str(item_id))
            continue
        if not item.is_verifiable or item.is_verified:
            skipped.append(item.test.name if item.test else str(item_id))
            continue

        item.verified_at = datetime.utcnow()
        item.verified_by_id = current_user.id
        # Clear any prior send-back note on this item
        item.correction_note = None
        verified.append(item.test.name if item.test else str(item_id))
        touched_orders.add(item.order_id)

    # If every top-level item of an order is now verified → mark order approved
    for order_id in touched_orders:
        o = Order.query.get(order_id)
        if o and o.all_verified and o.status != OrderStatus.APPROVED:
            o.status = OrderStatus.APPROVED
            o.reported_at = datetime.utcnow()
            o.reported_by_id = current_user.id

    if verified:
        db.session.commit()
        log_action(
            'approve', 'order_item', 0,
            f'Verified {len(verified)} item(s): {", ".join(verified[:10])}'
        )

    if verified:
        flash(
            f'Verified {len(verified)} test(s): {", ".join(verified[:8])}'
            + (f' …and {len(verified) - 8} more' if len(verified) > 8 else ''),
            'success'
        )
    if skipped:
        flash(
            f'Skipped {len(skipped)} item(s) that were not ready.',
            'warning'
        )

    return redirect(url_for('lab.verify_queue'))


# ============================================================
# SEND BACK (single item)
# ============================================================
@lab_bp.route('/verify/send-back/<int:item_id>', methods=['POST'])
@login_required
def send_back_item(item_id):
    """Send a single top-level item back for correction."""
    from modules.orders.models import OrderItem, Order, OrderStatus

    if not _can_verify():
        flash('Not allowed.', 'danger')
        return redirect(url_for('lab.verify_queue'))

    item = OrderItem.query.get_or_404(item_id)
    if item.is_child:
        flash('Cannot send back a panel child — send back the panel.', 'warning')
        return redirect(url_for('lab.verify_queue'))

    reason = (request.form.get('reason') or '').strip()
    if not reason:
        flash('Please provide a reason.', 'warning')
        return redirect(url_for('lab.verify_queue'))

    item.correction_note = reason
    item.correction_at = datetime.utcnow()
    item.correction_by_id = current_user.id
    # Clear verification so re-approval is required
    item.verified_at = None
    item.verified_by_id = None

    # Set the order's status to 'correction' (unless it's already there)
    order = item.order
    if order.status != OrderStatus.CORRECTION:
        order.status = OrderStatus.CORRECTION
        order.correction_at = datetime.utcnow()
        order.correction_by_id = current_user.id
        order.correction_note = (
            f'{item.test.name if item.test else "Test"}: {reason}'
        )

    db.session.commit()

    log_action(
        'correction', 'order_item', item.id,
        f'Sent back {item.test.name if item.test else item.id} '
        f'for correction: {reason[:80]}'
    )

    flash(
        f'Sent back "{item.test.name if item.test else item.id}" for correction.',
        'info'
    )
    return redirect(url_for('lab.verify_queue'))


# ============================================================
# SEND BACK (bulk) — NEW
# ============================================================
@lab_bp.route('/verify/bulk-send-back', methods=['POST'])
@login_required
def bulk_send_back():
    """Send one or more top-level items back for correction.

    Expects form fields:
      item_ids (multiple values)
      reason   (single string, applied to all)

    Skips items that are panel children or not ready for verification.
    Each affected order is moved to 'correction' status.
    """
    from modules.orders.models import OrderItem, Order, OrderStatus

    if not _can_verify():
        flash('Not allowed.', 'danger')
        return redirect(url_for('lab.verify_queue'))

    item_ids = request.form.getlist('item_ids', type=int)
    reason = (request.form.get('reason') or '').strip()

    if not item_ids:
        flash('No items selected.', 'warning')
        return redirect(url_for('lab.verify_queue'))
    if not reason:
        flash('Please provide a reason.', 'warning')
        return redirect(url_for('lab.verify_queue'))

    sent = 0
    skipped = 0
    touched_orders = set()
    sent_names = []

    for item_id in item_ids:
        item = OrderItem.query.get(item_id)

        # Skip invalid items
        if not item or item.is_child:
            skipped += 1
            continue

        # Item must be either currently verifiable OR currently verified
        # (in case the pathologist wants to send back something already approved)
        if not item.is_verifiable and not item.is_verified:
            skipped += 1
            continue

        item.correction_note = reason
        item.correction_at = datetime.utcnow()
        item.correction_by_id = current_user.id
        # Clear verification so re-approval is required
        item.verified_at = None
        item.verified_by_id = None

        touched_orders.add(item.order_id)
        sent += 1
        sent_names.append(item.test.name if item.test else f'#{item_id}')

    # Mark each affected order as 'correction' if it isn't already
    for order_id in touched_orders:
        o = Order.query.get(order_id)
        if o and o.status != OrderStatus.CORRECTION:
            o.status = OrderStatus.CORRECTION
            o.correction_at = datetime.utcnow()
            o.correction_by_id = current_user.id
            o.correction_note = reason
        # Also clear order-level approval since at least one item is now unverified
        if o and o.reported_at and not o.all_verified:
            o.reported_at = None
            o.reported_by_id = None

    if sent:
        db.session.commit()
        log_action(
            'correction', 'order_item', 0,
            f'Bulk sent back {sent} item(s) for correction: {reason[:80]}'
        )
        flash(
            f'Sent back {sent} test(s) for correction: '
            f'{", ".join(sent_names[:8])}'
            + (f' …and {sent - 8} more' if sent > 8 else ''),
            'info'
        )
    if skipped:
        flash(f'Skipped {skipped} item(s) that were not eligible.', 'warning')
    if not sent and not skipped:
        flash('Nothing was sent back.', 'warning')

    return redirect(url_for('lab.verify_queue'))
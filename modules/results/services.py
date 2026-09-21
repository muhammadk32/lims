"""Business logic for results entry.

No HTTP, no flash, no redirect. Pure domain operations.
"""
from datetime import datetime

from extensions import db
from core.audit import log_action
from modules.orders.models import Order, OrderItem, OrderStatus


# ============================================================
# Save results for an order
# ============================================================
def save_order_results(order, form, user):
    """Apply submitted form values to order items.

    Behavior:
      - Saves every result_value_{item_id} and result_notes_{item_id}.
      - Clears per-item correction flags for anything now having a value.
      - If the order was APPROVED and any value changed → reset to COMPLETED
        and clear per-item verification. Returns ('reset', None).
      - If the order was CORRECTION and nothing still needs correction →
        clears order-level correction fields and moves to COMPLETED.
      - Auto-completes when all results are in.

    Returns a tuple (mode, payload):
      ('reset',    order)  — approval was reset (route should redirect to view)
      ('saved',    order)  — normal save
      ('nochange', order)  — nothing changed, still committed
    """
    was_approved = (order.status == OrderStatus.APPROVED)
    was_correction = (order.status == OrderStatus.CORRECTION)
    old_values = {i.id: i.result_value for i in order.items}

    # --- 1. Apply submitted values ---
    for item in order.items:
        value = form.get(f'result_value_{item.id}', '').strip()
        notes = form.get(f'result_notes_{item.id}', '').strip()
        item.result_value = value or None
        item.result_notes = notes or None

    # --- 2. Detect changes ---
    something_changed = any(
        old_values.get(item.id) != item.result_value
        for item in order.items
    )

    # --- 3. Clear correction flags on items that now have a value ---
    for item in order.items:
        if item.correction_note and item.result_value:
            item.correction_note = None
            item.correction_at = None
            item.correction_by_id = None

    # --- 4. If approved and edited → reset approval, return 'reset' ---
    if was_approved and something_changed:
        order.status = OrderStatus.COMPLETED
        order.reported_at = None
        order.reported_by_id = None

        for top in order.top_level_items:
            if top.is_verified:
                top.verified_at = None
                top.verified_by_id = None

        db.session.commit()
        log_action(
            'result', 'order', order.id,
            f'Edited results of approved order {order.order_code} '
            f'— approval reset, re-approval required',
            extra={'status': order.status},
        )
        return 'reset', order

    # --- 5. If was in CORRECTION and nothing still needs it → clear state ---
    if was_correction:
        still = any(
            getattr(t, 'needs_correction', False)
            for t in order.top_level_items
        ) or any(
            getattr(c, 'needs_correction', False)
            for t in order.top_level_items
            for c in t.children
        )
        if not still:
            order.correction_note = None
            order.correction_at = None
            order.correction_by_id = None
            if order.status == OrderStatus.CORRECTION:
                order.status = OrderStatus.COMPLETED

    # --- 6. Auto-complete when all results are in ---
    if order.all_results_done and order.status != OrderStatus.COMPLETED:
        order.status = OrderStatus.COMPLETED

    db.session.commit()
    log_action(
        'result', 'order', order.id,
        f'Entered results for order {order.order_code}',
        extra={'status': order.status},
    )
    return 'saved', order


# ============================================================
# Clear one result
# ============================================================
def clear_result_value(item, user):
    """Clear a single OrderItem's result and notes.

    Also clears parent verification (if any) and resets an approved
    order to COMPLETED.

    Returns (order, was_approved).
    Raises ValueError with a user-facing message if item isn't editable.
    """
    order = item.order
    if not order:
        raise ValueError('Item does not belong to any order.')
    if order.status == OrderStatus.CANCELLED:
        raise ValueError('Cannot edit a cancelled order.')

    item.result_value = None
    item.result_notes = None

    # Clear per-item verification on the top-level item this belongs to
    top = item if item.parent_item_id is None else item.parent
    if top and top.is_verified:
        top.verified_at = None
        top.verified_by_id = None

    was_approved = (order.status == OrderStatus.APPROVED)
    if was_approved:
        order.status = OrderStatus.COMPLETED
        order.reported_at = None
        order.reported_by_id = None

    db.session.commit()

    log_action(
        'result', 'order_item', item.id,
        f'Cleared result for item {item.id} on order {order.order_code}',
        extra={'order_id': order.id},
    )
    return order, was_approved


# ============================================================
# Patient history
# ============================================================
def get_patient_orders(patient_id):
    """Return non-cancelled orders for a patient, newest first."""
    return (
        Order.query
        .filter(Order.patient_id == patient_id)
        .filter(Order.status != OrderStatus.CANCELLED)
        .order_by(Order.id.desc())
        .all()
    )
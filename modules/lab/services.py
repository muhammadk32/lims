"""Business logic for lab verification.

No HTTP, no flash, no redirect. Pure domain operations.
"""
from datetime import datetime

from extensions import db
from core.audit import log_action
from modules.orders.models import Order, OrderItem, OrderStatus


def can_verify(user):
    """Only admin and doctor (pathologist) may verify/approve."""
    return bool(user and user.is_authenticated and user.role in ('admin', 'doctor'))


def item_label(item):
    """Human-readable label for an OrderItem."""
    return item.test.name if item.test else f'#{item.id}'


def label_list(names, limit=8):
    """Join first N labels, with '…and X more' suffix if needed."""
    head = ', '.join(names[:limit])
    extra = f' …and {len(names) - limit} more' if len(names) > limit else ''
    return head + extra


def approve_items(items, user):
    """Mark items verified and promote their orders to APPROVED when ready.

    Returns the list of item labels that were verified.
    """
    if not items:
        return []

    now = datetime.utcnow()
    for item in items:
        item.verified_at = now
        item.verified_by_id = user.id
        item.correction_note = None

    touched_order_ids = {i.order_id for i in items}
    for oid in touched_order_ids:
        order = Order.query.get(oid)
        if order and order.all_verified and order.status != OrderStatus.APPROVED:
            order.status = OrderStatus.APPROVED
            order.reported_at = now
            order.reported_by_id = user.id

    db.session.commit()

    labels = [item_label(i) for i in items]
    log_action(
        'approve', 'order_item', 0,
        f'Verified {len(items)} item(s): {", ".join(labels[:10])}'
    )
    return labels


def send_back_items(items, reason, user, *, order_note_mode='single'):
    """Send items back for correction.

    order_note_mode:
      'single'  → set order.correction_note to '<test>: <reason>'
      'bulk'    → set order.correction_note to just <reason>
      'skip'    → don't touch order.correction_note

    Panels: when a top-level panel is sent back, each child is ALSO
    flagged so the results-entry page renders inputs for them.
    """
    now = datetime.utcnow()
    touched_order_ids = set()

    for item in items:
        item.correction_note = reason
        item.correction_at = now
        item.correction_by_id = user.id
        item.verified_at = None
        item.verified_by_id = None
        touched_order_ids.add(item.order_id)

        # Propagate correction to every panel child so the technician
        # can re-enter results for each parameter.
        if item.has_children:
            for child in item.children:
                child.correction_note = reason
                child.correction_at = now
                child.correction_by_id = user.id

    for oid in touched_order_ids:
        order = Order.query.get(oid)
        if not order:
            continue
        if order.status != OrderStatus.CORRECTION:
            order.status = OrderStatus.CORRECTION
            order.correction_at = now
            order.correction_by_id = user.id
            if order_note_mode == 'single' and items:
                order.correction_note = f'{item_label(items[0])}: {reason}'
            elif order_note_mode == 'bulk':
                order.correction_note = reason
        # If order was previously approved but is no longer fully verified,
        # clear the approval stamp.
        if order.reported_at and not order.all_verified:
            order.reported_at = None
            order.reported_by_id = None

    return list(touched_order_ids)
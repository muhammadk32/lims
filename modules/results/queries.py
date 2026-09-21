"""Query helpers for results entry — pure data-fetching.

No HTTP, no flash, no commits.
"""
from sqlalchemy import or_

from modules.orders.models import Order, OrderItem, OrderStatus


# ============================================================
# Pending / leaf logic
# ============================================================
def pending_items_for_order(order):
    """Return the top-level items that still need technician action.

    An item needs action when ANY of:
      - it has no result yet (missing), OR
      - a pathologist sent it back for correction (needs_correction)

    For panels, needs action when any child is missing a result
    OR any child was sent back for correction.

    Items already verified are hidden.
    """
    result = []
    for top in order.top_level_items:
        if top.is_verified:
            continue

        # Correction flag on the top-level item itself → always pending.
        if getattr(top, 'needs_correction', False):
            result.append(top)
            continue

        if top.has_children:
            # Panel: pending if any child is missing a result OR
            # any child was sent back for correction.
            if any(
                (not c.result_value) or getattr(c, 'needs_correction', False)
                for c in top.children
            ):
                result.append(top)
        else:
            # Standalone: pending only if result is missing.
            # (If filled and unverified, that's the pathologist's job.)
            if not top.result_value:
                result.append(top)
    return result


def order_leaf_counts(order):
    """Return (total_leaves, done_leaves) — children count as leaves."""
    total = 0
    done = 0
    for top in order.top_level_items:
        if top.has_children:
            total += len(top.children)
            done += sum(1 for c in top.children if c.result_value)
        else:
            total += 1
            if top.result_value:
                done += 1
    return total, done


# ============================================================
# Pending orders list
# ============================================================
def list_pending_orders(q='', order_filter=''):
    """Return the list of orders that still have pending work.

    An order appears when:
      (a) at least one of its leaf tests has a missing result, OR
      (b) its status is 'correction'.
    Approved orders are hidden. Cancelled orders are excluded.

    Each returned order gets a `pending_items` attribute attached.
    """
    from modules.patients.models import Patient

    query = Order.query.filter(Order.status != OrderStatus.CANCELLED)

    if q:
        like = f'%{q}%'
        query = (
            query
            .outerjoin(Patient, Order.patient_id == Patient.id)
            .filter(or_(
                Order.order_code.ilike(like),
                Patient.full_name.ilike(like),
                Patient.patient_code.ilike(like),
            ))
        )

    candidates = query.order_by(Order.id.desc()).all()

    pending_orders = []
    for order in candidates:
        # (b) Correction → always show
        if order.status == OrderStatus.CORRECTION:
            order.pending_items = pending_items_for_order(order)
            pending_orders.append(order)
            continue

        # Approved orders → hide entirely
        if order.status == OrderStatus.APPROVED:
            continue

        # Otherwise: show only if some top-level item still needs action
        items = pending_items_for_order(order)
        if items:
            order.pending_items = items
            pending_orders.append(order)

    # Optional filter: 'empty' (nothing done) or 'incomplete' (some done)
    if order_filter in ('empty', 'incomplete'):
        filtered = []
        for order in pending_orders:
            total_leaves, done_leaves = order_leaf_counts(order)
            is_empty = (done_leaves == 0)
            is_incomplete = (0 < done_leaves < total_leaves)

            if order_filter == 'empty' and is_empty:
                filtered.append(order)
            elif order_filter == 'incomplete' and is_incomplete:
                filtered.append(order)

        pending_orders = filtered

    return pending_orders
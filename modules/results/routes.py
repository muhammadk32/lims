from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required

from extensions import db
from core.decorators import permission_required
from core.audit import log_action
from modules.results import results_bp
from modules.results.models import Result
from modules.orders.models import Order, OrderItem, OrderStatus


# ============================================================
# Helpers — per-order pending logic
# ============================================================
def _pending_items_for_order(order):
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
            # (If it's filled and unverified, that's the pathologist's job.)
            if not top.result_value:
                result.append(top)
    return result


def _order_leaf_counts(order):
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


@results_bp.route('/')
@login_required
def index():
    """Pending results — grouped by ORDER.

    Shows ONE row per order. Expanding the row (click [+]) reveals
    the top-level tests that still need technician action:

      - Missing results (not yet entered)
      - Panels with missing children
      - Any item sent back for correction

    Items already verified by a pathologist are hidden, even if
    their results are shown elsewhere.

    An order appears here when:
      (a) at least one of its leaf tests has a missing result, OR
      (b) its status is 'correction' (pathologist sent it back).

    Query params:
      ?q=...       search by Lab #, patient name, patient code, or test code
      ?order=...   filter: 'empty' (nothing done) or 'incomplete' (some done)
    """
    from sqlalchemy import or_
    from modules.patients.models import Patient

    q = request.args.get('q', '').strip()
    order_filter = request.args.get('order', '').strip()

    # --- 1. Base query: orders, not items ---
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

    # --- 2. Compute which orders still have pending work ---
    pending_orders = []
    for order in candidates:

        # (b) Correction state → always show
        if order.status == OrderStatus.CORRECTION:
            order.pending_items = _pending_items_for_order(order)
            pending_orders.append(order)
            continue

        # Approved orders → hide entirely
        if order.status == OrderStatus.APPROVED:
            continue

        # Otherwise: show only if some top-level item still needs action
        pending_items = _pending_items_for_order(order)
        if pending_items:
            order.pending_items = pending_items
            pending_orders.append(order)

    # --- 3. Optional order-level filter ---
    if order_filter in ('empty', 'incomplete'):
        filtered = []
        for order in pending_orders:
            total_leaves, done_leaves = _order_leaf_counts(order)
            is_empty = (done_leaves == 0)
            is_incomplete = (0 < done_leaves < total_leaves)

            if order_filter == 'empty' and is_empty:
                filtered.append(order)
            elif order_filter == 'incomplete' and is_incomplete:
                filtered.append(order)

        pending_orders = filtered

    return render_template(
        'results/index.html',
        pending_orders=pending_orders,
        q=q,
        order_filter=order_filter,
    )


@results_bp.route('/enter/<int:order_id>', methods=['GET', 'POST'])
@login_required
@permission_required('enter_results')
def enter(order_id):
    """Enter or update results for every item in an order.

    Behaviour on POST:
      - Saves all result values and notes for the order's items.
      - Clears per-item correction flags for anything re-saved.
      - If the order was already APPROVED, editing any value resets
        it to COMPLETED and clears reported_at / reported_by_id.
      - Verified items are cleared back to 'entered' when edited.
      - If the order was CORRECTION and nothing needs correction any
        more, it moves back to COMPLETED (ready for re-verification).
    """
    order = Order.query.get_or_404(order_id)

    if request.method == 'POST':
        was_approved = (order.status == OrderStatus.APPROVED)
        was_correction = (order.status == OrderStatus.CORRECTION)
        old_values = {i.id: i.result_value for i in order.items}

        # --- Save every item's value + notes ---
        for item in order.items:
            value = request.form.get(f'result_value_{item.id}', '').strip()
            notes = request.form.get(f'result_notes_{item.id}', '').strip()
            item.result_value = value or None
            item.result_notes = notes or None

        # --- Detect changes ---
        something_changed = False
        for item in order.items:
            if old_values.get(item.id) != item.result_value:
                something_changed = True
                break

        # --- Clear correction flags on any item that now has a value ---
        for item in order.items:
            if item.correction_note and item.result_value:
                item.correction_note = None
                item.correction_at = None
                item.correction_by_id = None

        # --- If editing an APPROVED order → reset approval ---
        if was_approved and something_changed:
            order.status = OrderStatus.COMPLETED
            order.reported_at = None
            order.reported_by_id = None

            for top in order.top_level_items:
                if top.is_verified:
                    top.verified_at = None
                    top.verified_by_id = None

            log_action(
                'result', 'order', order.id,
                f'Edited results of approved order {order.order_code} '
                f'— approval reset, re-approval required',
                extra={'status': order.status},
            )

            db.session.commit()
            flash(
                f'Results updated for Lab # {order.order_code}. '
                f'The report must be re-approved.',
                'warning'
            )
            return redirect(url_for('orders.view_order', order_id=order.id))

        # --- If order was in CORRECTION and nothing still needs it → clear state ---
        if was_correction:
            still_needs_correction = any(
                getattr(t, 'needs_correction', False)
                for t in order.top_level_items
            ) or any(
                getattr(c, 'needs_correction', False)
                for t in order.top_level_items
                for c in t.children
            )

            if not still_needs_correction:
                order.correction_note = None
                order.correction_at = None
                order.correction_by_id = None
                if order.status == OrderStatus.CORRECTION:
                    order.status = OrderStatus.COMPLETED

        # --- Normal path — auto-complete when all results are in ---
        if order.all_results_done and order.status != OrderStatus.COMPLETED:
            order.status = OrderStatus.COMPLETED

        db.session.commit()

        log_action('result', 'order', order.id,
                   f'Entered results for order {order.order_code}',
                   extra={'status': order.status})

        flash(f'Results saved for Lab # {order.order_code}.', 'success')
        return redirect(url_for('results.index'))

    return render_template('results/enter.html', order=order)


@results_bp.route('/report/<int:order_id>')
@login_required
def report(order_id):
    """Printable result report for an order."""
    order = Order.query.get_or_404(order_id)
    return render_template('results/report.html', order=order)


# ============================================================
# CLEAR SINGLE RESULT
# ============================================================
@results_bp.route('/clear/<int:item_id>', methods=['POST'])
@login_required
@permission_required('enter_results')
def clear_result(item_id):
    """Clear the result_value and result_notes of a single OrderItem."""
    item = OrderItem.query.get_or_404(item_id)
    order = item.order

    if not order:
        flash('Item does not belong to any order.', 'danger')
        return redirect(url_for('results.index'))

    if order.status == OrderStatus.CANCELLED:
        flash('Cannot edit a cancelled order.', 'warning')
        return redirect(url_for('orders.view_order', order_id=order.id))

    item.result_value = None
    item.result_notes = None

    # Clear per-item verification on the top-level item this belongs to
    top = item if item.parent_item_id is None else item.parent
    if top and top.is_verified:
        top.verified_at = None
        top.verified_by_id = None

    if order.status == OrderStatus.APPROVED:
        order.status = OrderStatus.COMPLETED
        order.reported_at = None
        order.reported_by_id = None
        flash(
            f'Result cleared for Lab # {order.order_code}. '
            f'The report must be re-approved.',
            'warning'
        )
    else:
        flash(f'Result cleared for Lab # {order.order_code}.', 'info')

    db.session.commit()

    log_action(
        'result', 'order_item', item.id,
        f'Cleared result for item {item.id} on order {order.order_code}',
        extra={'order_id': order.id},
    )

    return redirect(url_for('results.enter', order_id=order.id))


# ============================================================
# PATIENT HISTORY
# ============================================================
@results_bp.route('/history/<int:patient_id>')
@login_required
def patient_history(patient_id):
    """Show all past results for a patient, ordered newest first."""
    from modules.patients.models import Patient
    from modules.results.validators import check_result as check_flag

    patient = Patient.query.get_or_404(patient_id)

    orders = (
        Order.query
        .filter(Order.patient_id == patient.id)
        .filter(Order.status != OrderStatus.CANCELLED)
        .order_by(Order.id.desc())
        .all()
    )

    return render_template(
        'results/history.html',
        patient=patient,
        orders=orders,
        check_flag=check_flag,
    )
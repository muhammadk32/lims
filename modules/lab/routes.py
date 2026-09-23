"""
Laboratory workflow routes.

The verify queue groups pending items by their parent order, so the
pathologist sees one row per order (expandable) instead of one row
per test.

Routes are thin: parse request → call service → flash → redirect.
Business logic lives in services.py; query building in queries.py.
"""
from datetime import date

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from extensions import db
from core.decorators import permission_required
from core.audit import log_action
from . import lab_bp
from . import queries as q
from . import services as svc


# ============================================================
# Guard
# ============================================================
def _deny(msg):
    """Return a redirect response if the user can't verify, else None."""
    if svc.can_verify(current_user):
        return None
    flash(msg, 'danger')
    return redirect(url_for('dashboard.index'))


# ============================================================
# VERIFY QUEUE
# ============================================================
@lab_bp.route('/verify')
@login_required
@permission_required('view_reports')
def verify_queue():
    """List orders with pending items awaiting pathologist verification."""
    denied = _deny('Only a pathologist or admin can access the verification queue.')
    if denied:
        return denied

    search = request.args.get('q', '').strip()
    today = date.today()
    default_from, default_to = q.default_date_range()

    date_from = q.parse_date(
        request.args.get('date_from', '').strip(), default_from)
    date_to = q.parse_date(
        request.args.get('date_to', '').strip(), default_to)

    items = q.get_verify_queue_items(search, date_from, date_to)
    orders = q.group_by_order(items)

    # Attach the pending items to each order so the template can expand them
    for order in orders:
        order.pending_items = [i for i in items if i.order_id == order.id]

    return render_template(
        'lab/verify.html',
        items=items,
        orders=orders,
        q=search,
        date_from=date_from.strftime('%Y-%m-%d'),
        date_to=date_to.strftime('%Y-%m-%d'),
        today=today.strftime('%Y-%m-%d'),
    )


# ============================================================
# BULK APPROVE
# ============================================================
@lab_bp.route('/verify/bulk-approve', methods=['POST'])
@login_required
def bulk_approve():
    """Verify one or more top-level items."""
    denied = _deny('Only a pathologist or admin can approve reports.')
    if denied:
        return denied

    item_ids = request.form.getlist('item_ids', type=int)
    if not item_ids:
        flash('No items selected.', 'warning')
        return redirect(url_for('lab.verify_queue'))

    items, skipped = q.load_items_for_action(item_ids, require_ready=True)
    labels = svc.approve_items(items, current_user)

    if labels:
        flash(f'Verified {len(labels)} test(s): {svc.label_list(labels)}', 'success')
    if skipped:
        flash(f'Skipped {skipped} item(s) that were not ready.', 'warning')

    return redirect(url_for('lab.verify_queue'))


# ============================================================
# SEND BACK (single)
# ============================================================
@lab_bp.route('/verify/send-back/<int:item_id>', methods=['POST'])
@login_required
def send_back_item(item_id):
    """Send a single top-level item back for correction."""
    denied = _deny('Not allowed.')
    if denied:
        return denied

    from modules.orders.models import OrderItem

    item = OrderItem.query.get_or_404(item_id)
    if item.is_child:
        flash('Cannot send back a panel child — send back the panel.', 'warning')
        return redirect(url_for('lab.verify_queue'))

    reason = (request.form.get('reason') or '').strip()
    if not reason:
        flash('Please provide a reason.', 'warning')
        return redirect(url_for('lab.verify_queue'))

    svc.send_back_items([item], reason, current_user, order_note_mode='single')
    db.session.commit()

    log_action(
        'correction', 'order_item', item.id,
        f'Sent back {svc.item_label(item)} for correction: {reason[:80]}'
    )
    flash(f'Sent back "{svc.item_label(item)}" for correction.', 'info')
    return redirect(url_for('lab.verify_queue'))


# ============================================================
# SEND BACK (bulk)
# ============================================================
@lab_bp.route('/verify/bulk-send-back', methods=['POST'])
@login_required
def bulk_send_back():
    """Send one or more top-level items back for correction."""
    denied = _deny('Not allowed.')
    if denied:
        return denied

    item_ids = request.form.getlist('item_ids', type=int)
    reason = (request.form.get('reason') or '').strip()

    if not item_ids:
        flash('No items selected.', 'warning')
        return redirect(url_for('lab.verify_queue'))
    if not reason:
        flash('Please provide a reason.', 'warning')
        return redirect(url_for('lab.verify_queue'))

    items, skipped = q.load_items_for_action(item_ids, require_ready=False)
    svc.send_back_items(items, reason, current_user, order_note_mode='bulk')

    labels = [svc.item_label(i) for i in items]
    if items:
        db.session.commit()
        log_action(
            'correction', 'order_item', 0,
            f'Bulk sent back {len(items)} item(s) for correction: {reason[:80]}'
        )
        flash(f'Sent back {len(labels)} test(s) for correction: '
              f'{svc.label_list(labels)}', 'info')
    if skipped:
        flash(f'Skipped {skipped} item(s) that were not eligible.', 'warning')
    if not items and not skipped:
        flash('Nothing was sent back.', 'warning')

    return redirect(url_for('lab.verify_queue'))
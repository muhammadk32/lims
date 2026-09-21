"""Results entry, listing, and patient history routes.

Routes are thin: parse request → call service → flash → redirect.
Business logic lives in services.py; query building in queries.py.
"""
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required

from core.decorators import permission_required
from modules.results import results_bp
from modules.orders.models import Order, OrderItem, OrderStatus
from . import queries as q
from . import services as svc


# ============================================================
# PENDING RESULTS LIST
# ============================================================
@results_bp.route('/')
@login_required
def index():
    """Pending results — grouped by ORDER.

    Shows ONE row per order. Expanding the row (click [+]) reveals
    the top-level tests that still need technician action:

      - Missing results (not yet entered)
      - Panels with missing children
      - Any item sent back for correction

    Items already verified by a pathologist are hidden.

    Query params:
      ?q=...       search by Lab #, patient name, patient code
      ?order=...   filter: 'empty' or 'incomplete'
    """
    search = request.args.get('q', '').strip()
    order_filter = request.args.get('order', '').strip()

    pending_orders = q.list_pending_orders(q=search, order_filter=order_filter)

    return render_template(
        'results/index.html',
        pending_orders=pending_orders,
        q=search,
        order_filter=order_filter,
    )


# ============================================================
# ENTER RESULTS
# ============================================================
@results_bp.route('/enter/<int:order_id>', methods=['GET', 'POST'])
@login_required
@permission_required('enter_results')
def enter(order_id):
    """Enter or update results for every item in an order.

    On POST: delegates to services.save_order_results, then flashes
    and redirects based on the outcome ('reset' vs 'saved').
    """
    order = Order.query.get_or_404(order_id)

    if request.method == 'POST':
        mode, order = svc.save_order_results(order, request.form, None)

        if mode == 'reset':
            flash(
                f'Results updated for Lab # {order.order_code}. '
                f'The report must be re-approved.',
                'warning',
            )
            return redirect(url_for('orders.view_order', order_id=order.id))

        flash(f'Results saved for Lab # {order.order_code}.', 'success')
        return redirect(url_for('results.index'))

    return render_template('results/enter.html', order=order)


# ============================================================
# REPORT
# ============================================================
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
    try:
        order, was_approved = svc.clear_result_value(item, None)
    except ValueError as e:
        flash(str(e), 'warning')
        # Try to redirect to the order if we can find it
        order = item.order
        if order:
            return redirect(url_for('orders.view_order', order_id=order.id))
        return redirect(url_for('results.index'))

    if was_approved:
        flash(
            f'Result cleared for Lab # {order.order_code}. '
            f'The report must be re-approved.',
            'warning',
        )
    else:
        flash(f'Result cleared for Lab # {order.order_code}.', 'info')

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
    orders = svc.get_patient_orders(patient.id)

    return render_template(
        'results/history.html',
        patient=patient,
        orders=orders,
        check_flag=check_flag,
    )
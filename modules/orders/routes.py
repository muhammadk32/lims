"""
Order / Patient Registration routes.

Cross-module model imports are done INSIDE functions (lazy imports)
to prevent circular-import chains at startup.

Routes are thin: parse request → call service → flash → redirect.
Business logic lives in services.py; query building in queries.py.
"""
from datetime import datetime, date, timedelta

from flask import (
    render_template, request, redirect, url_for, flash, abort, jsonify
)
from flask_login import login_required, current_user

from core.decorators import permission_required
from . import orders_bp
from .models import Order, OrderStatus
from . import queries as q
from . import services as svc


# ---------- Helpers ----------
def _get_order_or_404(order_id):
    order = Order.query.get(order_id)
    if not order:
        abort(404)
    return order


# ============================================================
# DAILY LEDGER
# ============================================================
@orders_bp.route('/')
@login_required
def list_orders():
    today = date.today()

    date_from_str = request.args.get('date_from', '').strip() or today.strftime('%Y-%m-%d')
    date_to_str = request.args.get('date_to', '').strip() or today.strftime('%Y-%m-%d')

    date_from = q.parse_date(date_from_str) or today
    date_to = q.parse_date(date_to_str) or today
    date_from_str = date_from.strftime('%Y-%m-%d')
    date_to_str = date_to.strftime('%Y-%m-%d')

    search = request.args.get('q', '').strip()
    status = request.args.get('status', '').strip()
    paid_filter = request.args.get('paid', '').strip()

    orders, stats = q.get_ledger_orders(
        q=search, status=status, paid_filter=paid_filter,
        date_from=date_from, date_to=date_to,
    )

    return render_template(
        'orders/list.html',
        orders=orders,
        q=search,
        status=status,
        paid_filter=paid_filter,
        statuses=OrderStatus.CHOICES,
        date_from=date_from_str,
        date_to=date_to_str,
        stats=stats,
        today=today.strftime('%Y-%m-%d'),
    )


# ============================================================
# NEW ORDER
# ============================================================
@orders_bp.route('/new', methods=['GET', 'POST'])
@login_required
@permission_required('create_order')
def new_order():
    from modules.billing.models import PaymentMethod
    from modules.form_settings.helpers import get_form_config

    if request.method == 'POST':
        return _handle_new_order_post()

    return render_template(
        'orders/new.html',
        config=get_form_config(),
        doctors=q.get_doctors(),
        payment_methods=PaymentMethod.CHOICES,
        payment_method_labels=PaymentMethod.LABELS,
        now=datetime.now(),
    )


def _handle_new_order_post():
    from modules.patients.models import Patient
    from modules.tests.models import Test

    form = request.form
    patient_id = form.get('patient_id', type=int)

    # ---------- 1. Patient ----------
    if patient_id:
        patient = Patient.query.get(patient_id)
        if not patient:
            flash('Patient not found.', 'danger')
            return redirect(url_for('orders.new_order'))
    else:
        try:
            patient = svc.create_patient(form)
        except ValueError as e:
            flash(str(e), 'danger')
            return redirect(url_for('orders.new_order'))

    # ---------- 2. Tests ----------
    test_ids = form.getlist('test_ids', type=int)
    if not test_ids:
        flash('Please select at least one test.', 'danger')
        return redirect(url_for('orders.new_order'))

    tests = Test.query.filter(
        Test.id.in_(test_ids),
        Test.is_active == True,  # noqa: E712
    ).all()
    if not tests:
        flash('No valid tests selected.', 'danger')
        return redirect(url_for('orders.new_order'))

    # ---------- 3. Create order ----------
    try:
        order = svc.create_order(patient, tests, form, current_user)
    except ValueError as e:
        flash(str(e), 'danger')
        return redirect(url_for('orders.new_order'))

    # Warn if the discount wiped the full amount
    if order.subtotal > 0 and order.final_total <= 0.01:
        flash(
            'Note: order ' + order.order_code +
            ' has a 100pct discount - Rs 0 is due.',
            'warning',
        )
    flash(
        f'Lab # {order.order_code} created for {patient.full_name} '
        f'— Total: {order.final_total:.2f}',
        'success',
    )
    return redirect(url_for('orders.view_order', order_id=order.id))


# ============================================================
# AJAX APIs
# ============================================================
@orders_bp.route('/api/patient-lookup')
@login_required
def api_patient_lookup():
    phone = request.args.get('phone', '').strip()
    query = request.args.get('q', '').strip()
    return jsonify(q.lookup_patients(phone=phone, query=query))


@orders_bp.route('/api/test-search')
@login_required
def api_test_search():
    query = request.args.get('q', '').strip()
    return jsonify(q.search_tests(query))


@orders_bp.route('/api/doctors')
@login_required
def api_doctors():
    return jsonify(q.get_doctors())


@orders_bp.route('/api/test-prices')
@login_required
def api_test_prices():
    return jsonify(q.test_price_map())


# ============================================================
# VIEW / PRINT / STATUS / CANCEL
# ============================================================
@orders_bp.route('/<int:order_id>')
@login_required
def view_order(order_id):
    order = _get_order_or_404(order_id)
    return render_template(
        'orders/view.html',
        order=order,
        statuses=OrderStatus.CHOICES,
    )


@orders_bp.route('/<int:order_id>/print')
@login_required
def print_order(order_id):
    order = _get_order_or_404(order_id)

    # Block report if balance is due
    if order.balance_due > 0.01:
        from flask import flash
        flash(
            f'Report blocked - Rs {order.balance_due:.0f} balance due. '
            f'Please record payment first.',
            'warning',
        )
        from flask import redirect, url_for
        return redirect(url_for('orders.view_order', order_id=order.id))


    copy = request.args.get('copy', 'both').strip().lower()
    if copy not in ('patient', 'lab', 'both'):
        copy = 'both'

    auto = request.args.get('auto', '0') == '1'

    return render_template(
        'orders/print.html',
        order=order,
        timedelta=timedelta,
        copy=copy,
        auto=auto,
    )


@orders_bp.route('/<int:order_id>/status', methods=['POST'])
@login_required
@permission_required('update_order_status')
def change_status(order_id):
    order = _get_order_or_404(order_id)
    new_status = request.form.get('status', '').strip()

    if not svc.change_order_status(order, new_status, current_user):
        flash('Invalid status.', 'danger')
        return redirect(url_for('orders.view_order', order_id=order.id))

    flash(f'Lab # {order.order_code} status updated to "{new_status}".', 'success')
    return redirect(url_for('orders.view_order', order_id=order.id))


@orders_bp.route('/<int:order_id>/pay', methods=['POST'])
@login_required
@permission_required('record_payment')
def mark_paid(order_id):
    order = _get_order_or_404(order_id)
    svc.set_paid(order, True, current_user)
    flash('Payment flag set.', 'success')
    return redirect(url_for('orders.view_order', order_id=order.id))


@orders_bp.route('/<int:order_id>/unpay', methods=['POST'])
@login_required
@permission_required('record_payment')
def mark_unpaid(order_id):
    order = _get_order_or_404(order_id)
    svc.set_paid(order, False, current_user)
    flash('Payment flag removed.', 'info')
    return redirect(url_for('orders.view_order', order_id=order.id))


@orders_bp.route('/<int:order_id>/cancel', methods=['POST'])
@login_required
@permission_required('cancel_order')
def cancel_order(order_id):
    """Cancel an order and auto-refund any amount paid."""
    order = _get_order_or_404(order_id)
    reason = (request.form.get('reason') or '').strip()

    ok, error, refund = svc.cancel_order(order, reason, current_user)
    if not ok:
        flash(error, 'warning')
    else:
        if refund > 0:
            flash(
                f'Order {order.order_code} cancelled. '
                f'Refunded {refund:.2f} to patient.',
                'info',
            )
        else:
            flash(f'Order {order.order_code} cancelled. Nothing to refund.', 'info')
    return redirect(url_for('orders.view_order', order_id=order.id))


# ============================================================
# PATHOLOGIST APPROVAL / CORRECTION
# ============================================================
@orders_bp.route('/<int:order_id>/approve', methods=['POST'])
@login_required
def approve_report(order_id):
    if not svc.can_approve(current_user):
        flash('Only a pathologist or admin can approve reports.', 'danger')
        return redirect(url_for('orders.view_order', order_id=order_id))

    order = _get_order_or_404(order_id)
    ok, error = svc.approve_order(order, current_user)

    if not ok:
        flash(error, 'warning')
    else:
        flash(f'Report {order.order_code} approved.', 'success')
    return redirect(url_for('orders.view_order', order_id=order.id))


@orders_bp.route('/<int:order_id>/send-back', methods=['POST'])
@login_required
def send_back(order_id):
    if not svc.can_approve(current_user):
        flash('Only a pathologist or admin can send back reports.', 'danger')
        return redirect(url_for('orders.view_order', order_id=order_id))

    order = _get_order_or_404(order_id)
    reason = (request.form.get('reason') or '').strip()

    ok, error = svc.send_back_order(order, reason, current_user)
    if not ok:
        flash(error, 'warning')
    else:
        flash(f'Report {order.order_code} sent back for correction.', 'info')
    return redirect(url_for('orders.view_order', order_id=order.id))



@orders_bp.route('/api/referral-search')
@login_required
def api_referral_search():
    """Return referral suggestions matching ?q=."""
    from modules.referrals.queries import search_referrals
    query = request.args.get('q', '').strip()
    results = search_referrals(query)
    return jsonify([
        {
            'name': r.name,
            'clinic': r.clinic or '',
            'phone': r.phone or '',
            'times_used': r.times_used or 0,
        }
        for r in results
    ])
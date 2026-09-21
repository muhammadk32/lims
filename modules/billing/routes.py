"""
Billing routes.

Cross-module model imports are done INSIDE functions (lazy imports)
to prevent circular-import chains at startup.

Routes are thin: parse request → call service → flash → redirect.
Business logic lives in services.py; query building in queries.py.
"""
from datetime import datetime, timedelta, date

from flask import (
    render_template, request, redirect, url_for, flash, abort, send_file
)
from flask_login import login_required, current_user

from core.decorators import permission_required
from . import billing_bp
from .models import Payment, PaymentMethod
from . import queries as q
from . import services as svc


# ---------- Helpers ----------
def _get_order_or_404(order_id):
    from modules.orders.models import Order  # ← lazy
    order = Order.query.get(order_id)
    if not order:
        abort(404)
    return order


# ---------- Billing Dashboard ----------
@billing_bp.route('/')
@login_required
@permission_required('view_billing')
def index():
    search = request.args.get('q', '').strip()
    filter_by = request.args.get('filter', 'all').strip()

    orders, stats = q.list_billing_orders(q=search, filter_by=filter_by)

    return render_template(
        'billing/list.html',
        orders=orders,
        stats=stats,
        q=search,
        filter_by=filter_by,
    )


# ---------- Invoice View (HTML) ----------
@billing_bp.route('/invoice/<int:order_id>')
@login_required
@permission_required('view_billing')
def invoice(order_id):
    order = _get_order_or_404(order_id)
    from .invoice_generator import (
        LAB_NAME, LAB_ADDRESS, LAB_PHONE, LAB_EMAIL, LAB_WEBSITE, LAB_TAX_ID,
        DEFAULT_TAX_RATE,
    )
    return render_template(
        'billing/invoice.html',
        order=order,
        lab={
            'name': LAB_NAME,
            'address': LAB_ADDRESS,
            'phone': LAB_PHONE,
            'email': LAB_EMAIL,
            'website': LAB_WEBSITE,
            'tax_id': LAB_TAX_ID,
        },
        tax_rate=DEFAULT_TAX_RATE,
        methods=PaymentMethod.CHOICES,
        method_labels=PaymentMethod.LABELS,
    )


# ---------- Invoice PDF ----------
@billing_bp.route('/invoice/<int:order_id>/pdf')
@login_required
@permission_required('view_billing')
def invoice_pdf(order_id):
    order = _get_order_or_404(order_id)
    from .invoice_generator import generate_invoice_pdf  # ← lazy
    buffer = generate_invoice_pdf(order)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'invoice_INV-{order.order_code}.pdf',
        mimetype='application/pdf',
    )


@billing_bp.route('/invoice/<int:order_id>/view-pdf')
@login_required
@permission_required('view_billing')
def invoice_view_pdf(order_id):
    order = _get_order_or_404(order_id)
    from .invoice_generator import generate_invoice_pdf  # ← lazy
    buffer = generate_invoice_pdf(order)
    return send_file(buffer, mimetype='application/pdf', as_attachment=False)


# ---------- Record Payment ----------
@billing_bp.route('/order/<int:order_id>/pay', methods=['POST'])
@login_required
@permission_required('record_payment')
def add_payment(order_id):
    order = _get_order_or_404(order_id)

    try:
        amount = float(request.form.get('amount', 0))
    except (TypeError, ValueError):
        amount = 0

    method = request.form.get('method', PaymentMethod.CASH)
    ok, error, _payment = svc.record_payment(
        order=order,
        amount=amount,
        method=method,
        reference=request.form.get('reference', ''),
        notes=request.form.get('notes', ''),
        user=current_user,
    )

    if not ok:
        category = 'danger' if 'greater than 0' in error else 'warning'
        flash(error, category)
        return redirect(url_for('billing.invoice', order_id=order.id))

    flash(f'Payment of {amount:.2f} recorded.', 'success')
    return redirect(url_for('billing.invoice', order_id=order.id))


# ---------- Delete Payment ----------
@billing_bp.route('/payment/<int:payment_id>/delete', methods=['POST'])
@login_required
@permission_required('delete_payment')
def delete_payment(payment_id):
    payment = Payment.query.get(payment_id)
    if not payment:
        abort(404)

    order, _amount = svc.delete_payment(payment)
    flash('Payment removed.', 'info')
    return redirect(url_for('billing.invoice', order_id=order.id))


# ---------- Payment History (all) ----------
@billing_bp.route('/payments')
@login_required
@permission_required('view_billing')
def payments():
    page = request.args.get('page', 1, type=int)
    return render_template(
        'billing/payments.html',
        payments=q.paginate_payments(page=page),
    )


# ---------- Revenue Report ----------
@billing_bp.route('/revenue')
@login_required
@permission_required('view_revenue_reports')
def revenue():
    period = request.args.get('period', 'today')
    start_str = request.args.get('start', '')
    end_str = request.args.get('end', '')

    start_dt, end_dt, ok = q.resolve_period_range(period, start_str, end_str)
    if not ok:
        flash('Invalid date range.', 'danger')

    report = q.revenue_report(start_dt, end_dt)

    return render_template(
        'billing/revenue.html',
        period=period,
        start=start_dt.strftime('%Y-%m-%d'),
        end=end_dt.strftime('%Y-%m-%d'),
        method_labels=PaymentMethod.LABELS,
        **report,
    )
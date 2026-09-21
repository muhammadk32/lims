"""
Billing routes.

IMPORTANT: Cross-module model imports are done INSIDE functions
(lazy imports). This prevents circular-import chains at startup.
"""
from datetime import datetime, timedelta, date
from flask import (
    render_template, request, redirect, url_for, flash, abort, send_file
)
from flask_login import login_required, current_user
from sqlalchemy import func, or_
from extensions import db
from core.decorators import permission_required
from core.audit import log_action
from . import billing_bp
from .models import Payment, PaymentMethod   # same module — safe


# ---------- Helpers ----------
def _get_order_or_404(order_id):
    from modules.orders.models import Order   # ← lazy
    o = Order.query.get(order_id)
    if not o:
        abort(404)
    return o


def _sync_order_paid_flag(order):
    """Set order.paid based on payment balance."""
    order.paid = order.is_fully_paid


# ---------- Billing Dashboard ----------
@billing_bp.route('/')
@login_required
@permission_required('view_billing')
def index():
    from modules.orders.models import Order, OrderStatus   # ← lazy
    from modules.patients.models import Patient            # ← lazy

    q = request.args.get('q', '').strip()
    filter_by = request.args.get('filter', 'all').strip()

    query = Order.query.filter(Order.status != OrderStatus.CANCELLED)

    if q:
        like = f'%{q}%'
        query = query.join(Patient).filter(
            or_(
                Order.order_code.ilike(like),
                Patient.full_name.ilike(like),
                Patient.patient_code.ilike(like),
            )
        )

    orders = query.order_by(Order.id.desc()).all()

    if filter_by == 'unpaid':
        orders = [o for o in orders if o.payment_status == 'unpaid']
    elif filter_by == 'partial':
        orders = [o for o in orders if o.payment_status == 'partial']
    elif filter_by == 'paid':
        orders = [o for o in orders if o.payment_status == 'paid']

    today = date.today()
    total_orders = Order.query.filter(Order.status != OrderStatus.CANCELLED).count()
    total_billed = db.session.query(func.coalesce(func.sum(Order.total_amount), 0.0)) \
        .filter(Order.status != OrderStatus.CANCELLED).scalar()
    total_collected = db.session.query(func.coalesce(func.sum(Payment.amount), 0.0)).scalar()
    today_collected = db.session.query(func.coalesce(func.sum(Payment.amount), 0.0)) \
        .filter(func.date(Payment.created_at) == today).scalar()
    outstanding = max(0.0, total_billed - total_collected)

    stats = {
        'total_orders': total_orders,
        'total_billed': total_billed,
        'total_collected': total_collected,
        'today_collected': today_collected,
        'outstanding': outstanding,
    }

    return render_template(
        'billing/list.html',
        orders=orders,
        stats=stats,
        q=q,
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
    from .invoice_generator import generate_invoice_pdf   # ← lazy
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
    from .invoice_generator import generate_invoice_pdf   # ← lazy
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
    if amount <= 0:
        flash('Payment amount must be greater than 0.', 'danger')
        return redirect(url_for('billing.invoice', order_id=order.id))

    if amount > order.balance_due + 0.001:
        flash(f'Amount exceeds balance due (${order.balance_due:.2f}).', 'warning')
        return redirect(url_for('billing.invoice', order_id=order.id))

    method = request.form.get('method', PaymentMethod.CASH)
    if method not in PaymentMethod.CHOICES:
        method = PaymentMethod.CASH

    payment = Payment(
        order_id=order.id,
        amount=amount,
        method=method,
        reference=request.form.get('reference', '').strip() or None,
        notes=request.form.get('notes', '').strip() or None,
        received_by_id=current_user.id,
    )
    db.session.add(payment)
    db.session.flush()

    _sync_order_paid_flag(order)

    db.session.commit()

    log_action('payment', 'payment', payment.id,
               f'Received ${amount:.2f} ({method}) for {order.order_code}',
               extra={'order_id': order.id, 'method': method, 'amount': amount})

    flash(f'Payment of ${amount:.2f} recorded.', 'success')
    return redirect(url_for('billing.invoice', order_id=order.id))


# ---------- Delete Payment ----------
@billing_bp.route('/payment/<int:payment_id>/delete', methods=['POST'])
@login_required
@permission_required('delete_payment')
def delete_payment(payment_id):
    p = Payment.query.get(payment_id)
    if not p:
        abort(404)
    order = p.order
    p_amt = p.amount
    db.session.delete(p)
    db.session.flush()
    _sync_order_paid_flag(order)
    db.session.commit()

    log_action('delete', 'payment', payment_id,
               f'Deleted payment ${p_amt:.2f} from order {order.order_code}')

    flash('Payment removed.', 'info')
    return redirect(url_for('billing.invoice', order_id=order.id))


# ---------- Payment History (all) ----------
@billing_bp.route('/payments')
@login_required
@permission_required('view_billing')
def payments():
    page = request.args.get('page', 1, type=int)
    payments = Payment.query.order_by(Payment.id.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('billing/payments.html', payments=payments)


# ---------- Revenue Report ----------
@billing_bp.route('/revenue')
@login_required
@permission_required('view_revenue_reports')
def revenue():
    from modules.orders.models import Order, OrderStatus   # ← lazy

    period = request.args.get('period', 'today')
    start_str = request.args.get('start', '')
    end_str = request.args.get('end', '')

    today = date.today()
    if period == 'today':
        start_dt = datetime.combine(today, datetime.min.time())
        end_dt = datetime.combine(today, datetime.max.time())
    elif period == 'week':
        start_dt = datetime.combine(today - timedelta(days=today.weekday()), datetime.min.time())
        end_dt = datetime.now()
    elif period == 'month':
        start_dt = datetime(today.year, today.month, 1)
        end_dt = datetime.now()
    elif period == 'year':
        start_dt = datetime(today.year, 1, 1)
        end_dt = datetime.now()
    elif period == 'custom' and start_str and end_str:
        try:
            start_dt = datetime.strptime(start_str, '%Y-%m-%d')
            end_dt = datetime.strptime(end_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
        except ValueError:
            flash('Invalid date range.', 'danger')
            start_dt = datetime.combine(today, datetime.min.time())
            end_dt = datetime.now()
    else:
        start_dt = datetime.combine(today, datetime.min.time())
        end_dt = datetime.now()

    payments_in_range = (
        Payment.query
        .filter(Payment.created_at >= start_dt, Payment.created_at <= end_dt)
        .order_by(Payment.id.desc())
        .all()
    )
    total = sum(p.amount for p in payments_in_range)

    by_method = {}
    for p in payments_in_range:
        by_method.setdefault(p.method, 0.0)
        by_method[p.method] += p.amount

    by_day = {}
    for p in payments_in_range:
        key = p.created_at.strftime('%Y-%m-%d')
        by_day.setdefault(key, 0.0)
        by_day[key] += p.amount

    orders_created = Order.query.filter(
        Order.created_at >= start_dt,
        Order.created_at <= end_dt,
        Order.status != OrderStatus.CANCELLED,
    ).count()

    orders_billed = db.session.query(func.coalesce(func.sum(Order.total_amount), 0.0)) \
        .filter(
            Order.created_at >= start_dt,
            Order.created_at <= end_dt,
            Order.status != OrderStatus.CANCELLED,
        ).scalar()

    return render_template(
        'billing/revenue.html',
        period=period,
        start=start_dt.strftime('%Y-%m-%d'),
        end=end_dt.strftime('%Y-%m-%d'),
        payments=payments_in_range,
        total=total,
        by_method=by_method,
        method_labels=PaymentMethod.LABELS,
        by_day=dict(sorted(by_day.items())),
        orders_created=orders_created,
        orders_billed=orders_billed,
    )
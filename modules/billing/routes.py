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

    from datetime import date as _date
    today = _date.today()
    first_of_month = today.replace(day=1)

    return render_template(
        'billing/list.html',
        default_from=first_of_month.strftime('%Y-%m-%d'),
        default_to=today.strftime('%Y-%m-%d'),
    )


# ---------- Cash Summary Report ----------
@billing_bp.route('/report')
@login_required
@permission_required('view_billing')
def report():
    """Full cash summary report for a date range — opens in new tab."""
    from datetime import datetime as _dt, date as _date

    date_from_str = request.args.get('date_from', '').strip()
    date_to_str = request.args.get('date_to', '').strip()

    # Defaults: this month
    today = _date.today()
    try:
        date_from = _dt.strptime(date_from_str, '%Y-%m-%d').date() if date_from_str else today.replace(day=1)
    except (ValueError, TypeError):
        date_from = today.replace(day=1)
    try:
        date_to = _dt.strptime(date_to_str, '%Y-%m-%d').date() if date_to_str else today
    except (ValueError, TypeError):
        date_to = today

    orders, stats = q.list_billing_orders_for_range(date_from, date_to)

    return render_template(
        'billing/report.html',
        orders=orders,
        stats=stats,
        date_from=date_from.strftime('%d-%b-%Y'),
        date_to=date_to.strftime('%d-%b-%Y'),
        generated_at=__import__('datetime').datetime.now(),
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


# ---------- Excel Export ----------
@billing_bp.route('/report.xlsx')
@login_required
@permission_required('view_billing')
def report_xlsx():
    """Download the cash summary report as an Excel file."""
    from datetime import datetime as _dt, date as _date
    from io import BytesIO

    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
        from openpyxl.utils import get_column_letter
    except ImportError:
        flash('openpyxl not installed. Run: pip install openpyxl', 'danger')
        return redirect(url_for('billing.index'))

    date_from_str = request.args.get('date_from', '').strip()
    date_to_str = request.args.get('date_to', '').strip()
    today = _date.today()
    try:
        date_from = _dt.strptime(date_from_str, '%Y-%m-%d').date() if date_from_str else today.replace(day=1)
    except (ValueError, TypeError):
        date_from = today.replace(day=1)
    try:
        date_to = _dt.strptime(date_to_str, '%Y-%m-%d').date() if date_to_str else today
    except (ValueError, TypeError):
        date_to = today

    orders, stats = q.list_billing_orders_for_range(date_from, date_to)

    wb = Workbook()
    ws = wb.active
    ws.title = 'Cash Summary'

    bold_white = Font(bold=True, color='FFFFFF')
    bold = Font(bold=True)
    header_fill = PatternFill('solid', fgColor='212529')
    kpi_fill = PatternFill('solid', fgColor='F8F9FA')
    total_fill = PatternFill('solid', fgColor='E9ECEF')
    center = Alignment(horizontal='center', vertical='center')
    right = Alignment(horizontal='right')
    thin = Side(style='thin', color='6C757D')
    border_all = Border(left=thin, right=thin, top=thin, bottom=thin)

    ws['A1'] = 'Cash Summary Report'
    ws['A1'].font = Font(bold=True, size=14)
    ws.merge_cells('A1:J1')
    ws['A2'] = date_from.strftime('%d-%b-%Y') + ' to ' + date_to.strftime('%d-%b-%Y')
    ws['A2'].font = Font(size=10, italic=True, color='6C757D')
    ws.merge_cells('A2:J2')

    kpis = [
        ('Total Billed', stats['total_billed'], '#,##0.00'),
        ('Collected', stats['total_collected'], '#,##0.00'),
        ('Outstanding', stats['outstanding'], '#,##0.00'),
        ('Orders', stats['total_orders'], '0'),
    ]
    for i, (label, val, fmt) in enumerate(kpis, start=4):
        a = ws.cell(row=i, column=1, value=label)
        a.font = bold
        a.fill = kpi_fill
        a.border = border_all
        b = ws.cell(row=i, column=2, value=val)
        b.number_format = fmt
        b.fill = kpi_fill
        b.border = border_all

    headers = ['Invoice', 'Date', 'Patient', 'Patient #',
               'Total', 'Discount', 'Net', 'Paid', 'Balance', 'Status']
    start = 9
    for col, h in enumerate(headers, 1):
        c = ws.cell(row=start, column=col, value=h)
        c.font = bold_white
        c.fill = header_fill
        c.alignment = center
        c.border = border_all

    for i, o in enumerate(orders, 1):
        r = start + i
        cancelled = (o.status == 'cancelled')
        values = [
            'INV-' + o.order_code,
            o.created_at.strftime('%d/%m/%y') if o.created_at else '',
            o.patient.full_name,
            o.patient.patient_code,
            o.subtotal,
            o.discount_value,
            o.final_total,
            o.paid_amount,
            0 if cancelled else o.balance_due,
            'CANCELLED' if cancelled else o.status.upper(),
        ]
        for col, v in enumerate(values, 1):
            c = ws.cell(row=r, column=col, value=v)
            c.border = border_all
            if col in (5, 6, 7, 8, 9):
                c.number_format = '#,##0.00'
                c.alignment = right
            if cancelled:
                if col < 10:
                    c.font = Font(color='6C757D', strike=True)
                else:
                    c.font = Font(color='6C757D', bold=True)

    trow = start + len(orders) + 1
    ws.cell(row=trow, column=1, value='TOTALS')
    ws.cell(row=trow, column=5, value=stats['total_billed'])
    ws.cell(row=trow, column=7, value=stats['total_billed'])
    ws.cell(row=trow, column=8, value=stats['total_collected'])
    ws.cell(row=trow, column=9, value=stats['outstanding'])
    for col in range(1, 11):
        c = ws.cell(row=trow, column=col)
        c.font = bold
        c.fill = total_fill
        c.border = border_all
        if col in (5, 6, 7, 8, 9):
            c.number_format = '#,##0.00'

    widths = [14, 11, 24, 14, 12, 12, 12, 12, 12, 12]
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    ws.freeze_panes = ws.cell(row=start + 1, column=1)

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    filename = 'cash_summary_' + date_from.strftime('%Y%m%d') + '_' + date_to.strftime('%Y%m%d') + '.xlsx'
    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )

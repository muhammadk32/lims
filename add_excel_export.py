import os

# ============================================================
# 1. Add /billing/report.xlsx route
# ============================================================
rp = 'modules/billing/routes.py'
r = open(rp, encoding='utf-8').read()

if 'def report_xlsx' in r:
    print('SKIP - report_xlsx already exists')
else:
    route_code = open('_xlsx_route.py', encoding='utf-8').read() if os.path.exists('_xlsx_route.py') else None
    # Inline the route
    route_code = '''

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
'''
    if not r.endswith('\n'):
        r += '\n'
    r += route_code
    open(rp, 'w', encoding='utf-8').write(r)
    print('OK  - routes.py: /billing/report.xlsx added')


# ============================================================
# 2. Add Excel button to report.html
# ============================================================
tp = 'modules/billing/templates/billing/report.html'
t = open(tp, encoding='utf-8').read()

if 'report.xlsx' in t:
    print('SKIP - report.html already has Excel button')
else:
    anchor = '''      <button class="csr-btn csr-btn-primary" onclick="window.print()">
        Print
      </button>'''
    replacement = '''      <button class="csr-btn csr-btn-primary" onclick="window.print()">
        Print
      </button>
      <a class="csr-btn" href="#"
         onclick="var p=new URLSearchParams(location.search); location.href='/billing/report.xlsx?'+p.toString(); return false;">
        Excel
      </a>'''
    if anchor in t:
        t = t.replace(anchor, replacement, 1)
        open(tp, 'w', encoding='utf-8').write(t)
        print('OK  - report.html: Excel button added')
    else:
        print('WARN - report.html: Print button anchor not found')


print()
print('=' * 55)
print('Restart Flask, then:')
print('  1. Open /billing/')
print('  2. Pick dates, click Report')
print('  3. In the report tab, click the new Excel button')
print('  4. File downloads as cash_summary_YYYYMMDD_YYYYMMDD.xlsx')
print('=' * 55)

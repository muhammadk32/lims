"""
Add Due Collection report to Analytics hub.
"""
import os

# ============================================================
# 1. queries.py — due_report
# ============================================================
qp = 'modules/analytics/queries.py'
q = open(qp, encoding='utf-8').read()

if 'def due_report' not in q:
    new_fn = '''

# ============================================================
# 8. Due Collection — all orders with outstanding balance
# ============================================================
def due_report(date_from, date_to):
    """Return (orders_rows, totals) for orders with balance_due > 0.

    Orders fall off this list automatically once fully paid.
    """
    from modules.orders.models import Order, OrderStatus
    d_from, d_to = _parse_range(date_from, date_to)

    orders = (Order.query
        .filter(func.date(Order.created_at) >= d_from)
        .filter(func.date(Order.created_at) <= d_to)
        .filter(Order.status != OrderStatus.CANCELLED)
        .order_by(Order.id.asc())
        .all())

    rows = []
    for o in orders:
        due = round(o.balance_due or 0, 2)
        if due <= 0.01:
            continue
        days_old = 0
        try:
            if o.created_at:
                from datetime import date as _d
                days_old = (_d.today() - o.created_at.date()).days
        except Exception:
            pass
        rows.append({
            'order_id': o.id,
            'order_code': o.order_code,
            'date': o.created_at,
            'patient': o.patient.full_name,
            'patient_code': o.patient.patient_code,
            'phone': o.patient.phone or '-',
            'referral': o.referred_by_name or (o.doctor.full_name if o.doctor else '-'),
            'net': round(o.final_total or 0, 2),
            'paid': round(o.paid_amount or 0, 2),
            'due': due,
            'days_old': days_old,
        })

    rows.sort(key=lambda r: r['days_old'], reverse=True)

    totals = {
        'count': len(rows),
        'net': round(sum(r['net'] for r in rows), 2),
        'paid': round(sum(r['paid'] for r in rows), 2),
        'due': round(sum(r['due'] for r in rows), 2),
    }
    return rows, totals
'''
    open(qp, 'w', encoding='utf-8').write(q + new_fn)
    print('OK  - queries.py: due_report added')
else:
    print('SKIP - due_report exists')


# ============================================================
# 2. routes.py — /due and /due.xlsx
# ============================================================
rp = 'modules/analytics/routes.py'
r = open(rp, encoding='utf-8').read()

if 'def due(' not in r:
    new_routes = '''

# ============================================================
# Due Collection
# ============================================================
@analytics_bp.route('/due')
@login_required
@permission_required('view_reports')
def due():
    d_from, d_to = _range_from_request()
    rows, totals = q.due_report(d_from, d_to)
    return render_template('analytics/due.html',
                           **_ctx(d_from, d_to, rows=rows, totals=totals))


@analytics_bp.route('/due.xlsx')
@login_required
@permission_required('view_reports')
def due_xlsx():
    d_from, d_to = _range_from_request()
    rows, totals = q.due_report(d_from, d_to)

    data = []
    for r in rows:
        data.append([
            r['date'].strftime('%d-%b-%Y') if r['date'] else '',
            'INV-' + r['order_code'],
            r['patient'],
            r['patient_code'],
            r['phone'],
            r['referral'],
            r['net'],
            r['paid'],
            r['due'],
            r['days_old'],
        ])
    headers = ['Date', 'Invoice', 'Patient', 'Patient #', 'Phone',
               'Referral', 'Net', 'Paid', 'Due', 'Days Old']
    total_row = ['TOTAL', '', '', '', '', '',
                 totals['net'], totals['paid'], totals['due'], '']
    kpis = [
        ('Due Orders', totals['count'], '0'),
        ('Total Net', totals['net'], '#,##0.00'),
        ('Collected', totals['paid'], '#,##0.00'),
        ('Outstanding', totals['due'], '#,##0.00'),
    ]
    buf = build_workbook(
        'Due Collection Report',
        f"{d_from.strftime('%d-%b-%Y')} to {d_to.strftime('%d-%b-%Y')}",
        kpis, headers, data,
        widths=[14, 14, 22, 14, 14, 20, 12, 12, 12, 10],
        number_cols=[7, 8, 9],
        total_row=total_row,
    )
    return send_file(buf, as_attachment=True,
        download_name=f'due_{d_from:%Y%m%d}_{d_to:%Y%m%d}.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
'''
    open(rp, 'w', encoding='utf-8').write(r + new_routes)
    print('OK  - routes.py: due routes added')
else:
    print('SKIP - due routes exist')


# ============================================================
# 3. Template
# ============================================================
tpl = """{% extends 'analytics/_base.html' %}
{% block report_title %}Due Collection Report{% endblock %}
{% block excel_url %}{{ url_for('analytics.due_xlsx', date_from=date_from_raw, date_to=date_to_raw) }}{% endblock %}

{% block report_body %}

<table class="an-kpi">
  <tr>
    <td><div class="an-kpi-label">Due Orders</div><div class="an-kpi-value text-danger">{{ totals.count }}</div></td>
    <td><div class="an-kpi-label">Total Net</div><div class="an-kpi-value">{{ totals.net | money }}</div></td>
    <td><div class="an-kpi-label">Collected</div><div class="an-kpi-value text-success">{{ totals.paid | money }}</div></td>
    <td><div class="an-kpi-label">Outstanding</div><div class="an-kpi-value text-danger">{{ totals.due | money }}</div></td>
  </tr>
</table>

<table class="an-table">
  <thead>
    <tr>
      <th style="width: 110px;">Date</th>
      <th style="width: 110px;">Invoice #</th>
      <th style="width: 18%;">Patient Name</th>
      <th style="width: 14%;">Phone</th>
      <th>Referral</th>
      <th class="num" style="width: 90px;">Net</th>
      <th class="num" style="width: 90px;">Paid</th>
      <th class="num" style="width: 90px;">Due</th>
      <th class="text-center" style="width: 70px;">Age</th>
      <th class="text-end" style="width: 130px;">Action</th>
    </tr>
  </thead>
  <tbody>
    {% for r in rows %}
    <tr>
      <td class="muted">{{ r.date | localtime('%d/%m/%y %H:%M') }}</td>
      <td><a href="/orders/{{ r.order_id }}" class="text-decoration-none"><code>INV-{{ r.order_code }}</code></a></td>
      <td class="fw-semibold">{{ r.patient }}</td>
      <td class="muted">{{ r.phone }}</td>
      <td class="muted" style="font-size:0.76rem;">{{ r.referral }}</td>
      <td class="num">{{ r.net | money }}</td>
      <td class="num text-success">{{ r.paid | money }}</td>
      <td class="num fw-bold text-danger">{{ r.due | money }}</td>
      <td class="text-center muted" style="font-size:0.75rem;">
        {{ r.days_old }}d
      </td>
      <td class="text-end">
        <a href="{{ url_for('billing.invoice', order_id=r.order_id) }}"
           class="btn btn-sm btn-success" style="font-size:0.72rem;">
          <i class="bi bi-cash-coin"></i> Receive
        </a>
      </td>
    </tr>
    {% else %}
    <tr><td colspan="10" class="an-empty">
      <i class="bi bi-check2-circle fs-3 d-block mb-2 text-success"></i>
      No outstanding balances in this range.
    </td></tr>
    {% endfor %}
  </tbody>
  <tfoot>
    <tr>
      <td colspan="5" style="text-align:right; font-weight:700; text-transform:uppercase; letter-spacing:0.04em; padding-right:12px; border-top:2px solid #212529;">
        TOTAL
      </td>
      <td class="num" style="font-weight:700; border-top:2px solid #212529;">{{ totals.net | money }}</td>
      <td class="num" style="font-weight:700; border-top:2px solid #212529;">{{ totals.paid | money }}</td>
      <td class="num" style="font-weight:700; border-top:2px solid #212529;">{{ totals.due | money }}</td>
      <td colspan="2" style="border-top:2px solid #212529;"></td>
    </tr>
  </tfoot>
</table>
{% endblock %}
"""

os.makedirs('modules/analytics/templates/analytics', exist_ok=True)
open('modules/analytics/templates/analytics/due.html', 'w', encoding='utf-8').write(tpl)
print('OK  - due.html created')


# ============================================================
# 4. Add card to hub
# ============================================================
hp = 'modules/analytics/templates/analytics/index.html'
h = open(hp, encoding='utf-8').read()

if 'analytics.due' not in h:
    anchor = '''    <a class="rh-card" href="{{ url_for('analytics.commissions') }}">'''
    card = '''    <a class="rh-card" href="{{ url_for('analytics.due') }}">
      <span class="icon text-danger"><i class="bi bi-cash-stack"></i></span>
      <div class="name">Due Collection</div>
      <div class="desc">All orders with outstanding balance — oldest first. Payment removes the order.</div>
    </a>

'''
    if anchor in h:
        h = h.replace(anchor, card + anchor, 1)
        open(hp, 'w', encoding='utf-8').write(h)
        print('OK  - hub: Due Collection card added')
    else:
        print('WARN - hub anchor not found')


print()
print('=' * 55)
print('Done. Restart Flask and:')
print('  1. /analytics/ -> see new "Due Collection" card')
print('  2. Click it -> all unpaid orders with outstanding')
print('  3. Record payment -> order disappears')
print('=' * 55)

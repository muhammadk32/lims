# ============================================================
# Commission detail page - click doctor -> per-order breakdown
# ============================================================
import os

# ---------- 1. queries.py: commission_detail ----------
qp = 'modules/analytics/queries.py'
q = open(qp, encoding='utf-8').read()

if 'def commission_detail' not in q:
    new_fn = '''

# ============================================================
# 7. Commission Detail — per-order breakdown for one referral
# ============================================================
def commission_detail(referral_name, date_from, date_to):
    """Return (orders_rows, totals) for one referral — with commission per order."""
    from modules.orders.models import Order, OrderStatus
    d_from, d_to = _parse_range(date_from, date_to)

    orders = (Order.query
        .filter(func.date(Order.created_at) >= d_from)
        .filter(func.date(Order.created_at) <= d_to)
        .filter(Order.status != OrderStatus.CANCELLED)
        .order_by(Order.id.desc())
        .all())

    matched = []
    for o in orders:
        name = o.referred_by_name or (o.doctor.full_name if o.doctor else 'Walk-in')
        if name == referral_name and (o.commission_amount or 0) > 0:
            matched.append(o)

    rows = []
    for o in matched:
        pct = 0.0
        if (o.final_total or 0) > 0:
            pct = round((o.commission_amount / o.final_total) * 100, 2)
        rows.append({
            'order_id': o.id,
            'order_code': o.order_code,
            'date': o.created_at,
            'patient': o.patient.full_name,
            'patient_code': o.patient.patient_code,
            'phone': o.patient.phone or '-',
            'tests': o.item_count or 0,
            'billed': round(o.final_total or 0, 2),
            'commission_pct': pct,
            'commission': round(o.commission_amount or 0, 2),
            'commission_paid': bool(o.commission_paid),
            'commission_paid_at': o.commission_paid_at,
        })

    totals = {
        'orders': len(rows),
        'billed': round(sum(r['billed'] for r in rows), 2),
        'commission': round(sum(r['commission'] for r in rows), 2),
        'paid': round(sum(r['commission'] for r in rows if r['commission_paid']), 2),
        'outstanding': round(sum(r['commission'] for r in rows if not r['commission_paid']), 2),
    }
    return rows, totals
'''
    open(qp, 'w', encoding='utf-8').write(q + new_fn)
    print('OK  - queries.py: commission_detail added')
else:
    print('SKIP - commission_detail exists')


# ---------- 2. routes.py: /commissions/<name> and .xlsx ----------
rp = 'modules/analytics/routes.py'
r = open(rp, encoding='utf-8').read()

if 'def commission_detail' not in r:
    new_routes = '''

# ============================================================
# Commission Detail — per referral
# ============================================================
@analytics_bp.route('/commissions/<path:referral_name>')
@login_required
@permission_required('view_reports')
def commission_detail(referral_name):
    d_from, d_to = _range_from_request()
    rows, totals = q.commission_detail(referral_name, d_from, d_to)
    return render_template(
        'analytics/commission_detail.html',
        **_ctx(d_from, d_to, rows=rows, totals=totals, referral_name=referral_name),
    )


@analytics_bp.route('/commissions/<path:referral_name>.xlsx')
@login_required
@permission_required('view_reports')
def commission_detail_xlsx(referral_name):
    d_from, d_to = _range_from_request()
    rows, totals = q.commission_detail(referral_name, d_from, d_to)

    data = []
    for r in rows:
        data.append([
            r['date'].strftime('%d-%b-%Y %H:%M') if r['date'] else '',
            'INV-' + r['order_code'],
            r['patient'],
            r['patient_code'],
            r['phone'],
            r['tests'],
            r['billed'],
            r['commission_pct'],
            r['commission'],
            'PAID' if r['commission_paid'] else 'PENDING',
        ])
    headers = ['Date', 'Invoice', 'Patient', 'Patient #', 'Phone',
               'Tests', 'Billed', 'Comm %', 'Commission', 'Status']
    total_row = ['TOTAL', '', '', '', '', totals['orders'], totals['billed'],
                 '', totals['commission'], '']
    kpis = [
        ('Referral', referral_name, None),
        ('Orders', totals['orders'], '0'),
        ('Billed', totals['billed'], '#,##0.00'),
        ('Commission', totals['commission'], '#,##0.00'),
        ('Paid', totals['paid'], '#,##0.00'),
        ('Outstanding', totals['outstanding'], '#,##0.00'),
    ]
    buf = build_workbook(
        'Commission Detail: ' + referral_name,
        f"{d_from.strftime('%d-%b-%Y')} to {d_to.strftime('%d-%b-%Y')}",
        kpis, headers, data,
        widths=[18, 14, 22, 14, 14, 8, 12, 10, 14, 12],
        number_cols=[6, 7, 8, 9],
        total_row=total_row,
    )
    safe = ''.join(c for c in referral_name if c.isalnum() or c in ' -_')[:40]
    return send_file(buf, as_attachment=True,
        download_name=f'commission_{safe}_{d_from:%Y%m%d}_{d_to:%Y%m%d}.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
'''
    open(rp, 'w', encoding='utf-8').write(r + new_routes)
    print('OK  - routes.py: commission_detail routes added')
else:
    print('SKIP - commission_detail routes exist')


# ---------- 3. Create template ----------
tpl = """{% extends 'analytics/_base.html' %}
{% block report_title %}Commission Detail: {{ referral_name }}{% endblock %}
{% block excel_url %}/analytics/commissions/{{ referral_name }}.xlsx?date_from={{ date_from_raw }}&date_to={{ date_to_raw }}{% endblock %}

{% block report_body %}
<table class="an-kpi">
  <tr>
    <td><div class="an-kpi-label">Orders</div><div class="an-kpi-value">{{ totals.orders }}</div></td>
    <td><div class="an-kpi-label">Billed</div><div class="an-kpi-value">{{ totals.billed | money }}</div></td>
    <td><div class="an-kpi-label">Commission</div><div class="an-kpi-value fw-bold">{{ totals.commission | money }}</div></td>
    <td><div class="an-kpi-label">Paid</div><div class="an-kpi-value text-success">{{ totals.paid | money }}</div></td>
    <td><div class="an-kpi-label">Outstanding</div><div class="an-kpi-value text-danger">{{ totals.outstanding | money }}</div></td>
  </tr>
</table>

<table class="an-table">
  <thead>
    <tr>
      <th>Date</th>
      <th>Invoice</th>
      <th>Patient</th>
      <th>Patient #</th>
      <th>Phone</th>
      <th class="num">Tests</th>
      <th class="num">Billed</th>
      <th class="num">Comm %</th>
      <th class="num">Commission</th>
      <th>Status</th>
    </tr>
  </thead>
  <tbody>
    {% for r in rows %}
    <tr>
      <td class="muted">{{ r.date | localtime('%d/%m/%y %H:%M') }}</td>
      <td><a href="/orders/{{ r.order_id }}" class="text-decoration-none"><code>INV-{{ r.order_code }}</code></a></td>
      <td class="fw-semibold">{{ r.patient }}</td>
      <td class="muted">{{ r.patient_code }}</td>
      <td class="muted">{{ r.phone }}</td>
      <td class="num">{{ r.tests }}</td>
      <td class="num">{{ r.billed | money }}</td>
      <td class="num muted">{{ '%.2f'|format(r.commission_pct) }}%</td>
      <td class="num fw-semibold">{{ r.commission | money }}</td>
      <td>
        {% if r.commission_paid %}
          <span class="badge-ok">PAID</span>
        {% else %}
          <span class="badge-abn">PENDING</span>
        {% endif %}
      </td>
    </tr>
    {% else %}
    <tr><td colspan="10" class="an-empty">No commission data for this referral in this range.</td></tr>
    {% endfor %}
  </tbody>
  <tfoot>
    <tr>
      <td colspan="6">TOTAL</td>
      <td class="num">{{ totals.billed | money }}</td>
      <td></td>
      <td class="num">{{ totals.commission | money }}</td>
      <td></td>
    </tr>
  </tfoot>
</table>
{% endblock %}
"""

os.makedirs('modules/analytics/templates/analytics', exist_ok=True)
open('modules/analytics/templates/analytics/commission_detail.html', 'w', encoding='utf-8').write(tpl)
print('OK  - commission_detail.html created')


# ---------- 4. Make name clickable in commissions.html ----------
cp = 'modules/analytics/templates/analytics/commissions.html'
c = open(cp, encoding='utf-8').read()

old = '      <td class="fw-semibold">{{ r.name }}</td>'
new = '      <td class="fw-semibold"><a href="/analytics/commissions/{{ r.name }}" class="text-decoration-none">{{ r.name }}</a></td>'

if old in c and '/analytics/commissions/{{ r.name }}' not in c:
    c = c.replace(old, new, 1)
    open(cp, 'w', encoding='utf-8').write(c)
    print('OK  - commissions.html: names clickable')
elif '/analytics/commissions/{{ r.name }}' in c:
    print('SKIP - commissions.html already has links')
else:
    print('WARN - commissions.html anchor not found')


# ---------- 5. Add commission column to doctor_detail.html ----------
dp = 'modules/analytics/templates/analytics/doctor_detail.html'
d = open(dp, encoding='utf-8').read()

if 'Commission' not in d:
    # Add to header
    d = d.replace(
        '<th class="num">Due</th>',
        '<th class="num">Due</th>\n      <th class="num">Commission</th>',
        1,
    )
    # Add to body
    d = d.replace(
        '<td class="num text-danger">{% if r.due > 0 %}{{ r.due | money }}{% else %}—{% endif %}</td>',
        '<td class="num text-danger">{% if r.due > 0 %}{{ r.due | money }}{% else %}—{% endif %}</td>\n      <td class="num fw-semibold">{% if r.commission and r.commission > 0 %}{{ r.commission | money }}{% else %}—{% endif %}</td>',
        1,
    )
    # Add to footer
    d = d.replace(
        '<td class="num">{{ totals.due | money }}</td>',
        '<td class="num">{{ totals.due | money }}</td>\n      <td class="num">{{ totals.commission | money }}</td>',
        1,
    )
    open(dp, 'w', encoding='utf-8').write(d)
    print('OK  - doctor_detail.html: Commission column added')
else:
    print('SKIP - doctor_detail.html already has Commission')


# ---------- 6. Add commission to doctor_detail query ----------
qp2 = 'modules/analytics/queries.py'
q2 = open(qp2, encoding='utf-8').read()

if "'commission': round(o.commission_amount" not in q2:
    # Update doctor_detail_report to add commission per row
    q2 = q2.replace(
        "            'due': round(o.balance_due or 0, 2),\n            'status': o.status,",
        "            'due': round(o.balance_due or 0, 2),\n            'commission': round(o.commission_amount or 0, 2),\n            'status': o.status,",
        1,
    )
    # Add commission to totals
    q2 = q2.replace(
        "        'due': round(sum(r['due'] for r in rows), 2),\n    }",
        "        'due': round(sum(r['due'] for r in rows), 2),\n        'commission': round(sum(r['commission'] for r in rows), 2),\n    }",
        1,
    )
    open(qp2, 'w', encoding='utf-8').write(q2)
    print('OK  - doctor_detail_report: commission included')
else:
    print('SKIP - doctor_detail_report already has commission')


print()
print('=' * 55)
print('Done. Restart Flask and:')
print('  1. /analytics/commissions -> click any doctor name')
print('  2. See per-order commission breakdown')
print('  3. Excel button exports the detail')
print('=' * 55)

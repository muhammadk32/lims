# ============================================================
# Add doctor detail page — click doctor -> see patients
# ============================================================

# ---------- 1. queries.py: add doctor_detail_report ----------
qp = 'modules/analytics/queries.py'
q = open(qp, encoding='utf-8').read()

if 'def doctor_detail_report' not in q:
    new_fn = '''

# ============================================================
# 5. Doctor Detail — patients for one referral
# ============================================================
def doctor_detail_report(referral_name, date_from, date_to):
    """Return (orders_rows, totals) for one referral within a range."""
    from modules.orders.models import Order, OrderStatus
    d_from, d_to = _parse_range(date_from, date_to)

    orders = (Order.query
        .filter(func.date(Order.created_at) >= d_from)
        .filter(func.date(Order.created_at) <= d_to)
        .filter(Order.status != OrderStatus.CANCELLED)
        .order_by(Order.id.desc())
        .all())

    # Filter by referral (match either referred_by_name OR doctor.full_name)
    matched = []
    for o in orders:
        name = o.referred_by_name or (o.doctor.full_name if o.doctor else 'Walk-in')
        if name == referral_name:
            matched.append(o)

    rows = []
    for o in matched:
        tests = ', '.join(i.test.name for i in o.top_level_items if i.test)
        rows.append({
            'order_id': o.id,
            'order_code': o.order_code,
            'date': o.created_at,
            'patient': o.patient.full_name,
            'patient_code': o.patient.patient_code,
            'phone': o.patient.phone or '-',
            'age': o.patient.compute_age() or '-',
            'gender': o.patient.gender or '-',
            'tests': tests,
            'test_count': o.item_count or 0,
            'billed': round(o.final_total or 0, 2),
            'collected': round(o.paid_amount or 0, 2),
            'due': round(o.balance_due or 0, 2),
            'status': o.status,
        })

    totals = {
        'orders': len(rows),
        'patients': len(set(r['patient_code'] for r in rows)),
        'tests': sum(r['test_count'] for r in rows),
        'billed': round(sum(r['billed'] for r in rows), 2),
        'collected': round(sum(r['collected'] for r in rows), 2),
        'due': round(sum(r['due'] for r in rows), 2),
    }
    return rows, totals
'''
    with open(qp, 'w', encoding='utf-8') as f:
        f.write(q + new_fn)
    print('OK  - queries.py: doctor_detail_report added')
else:
    print('SKIP - queries.py already has doctor_detail_report')


# ---------- 2. routes.py: add /doctors/<name> route ----------
rp = 'modules/analytics/routes.py'
r = open(rp, encoding='utf-8').read()

if 'def doctor_detail' not in r:
    from urllib.parse import quote
    new_route = '''

# ============================================================
# Doctor Detail
# ============================================================
@analytics_bp.route('/doctors/<path:referral_name>')
@login_required
@permission_required('view_reports')
def doctor_detail(referral_name):
    """Detail report — all patients and orders for one referral."""
    d_from, d_to = _range_from_request()
    rows, totals = q.doctor_detail_report(referral_name, d_from, d_to)
    return render_template(
        'analytics/doctor_detail.html',
        **_ctx(d_from, d_to, rows=rows, totals=totals, referral_name=referral_name),
    )


@analytics_bp.route('/doctors/<path:referral_name>.xlsx')
@login_required
@permission_required('view_reports')
def doctor_detail_xlsx(referral_name):
    d_from, d_to = _range_from_request()
    rows, totals = q.doctor_detail_report(referral_name, d_from, d_to)

    data = []
    for r in rows:
        data.append([
            r['date'].strftime('%d-%b-%Y %H:%M') if r['date'] else '',
            'INV-' + r['order_code'],
            r['patient'],
            r['patient_code'],
            r['phone'],
            r['age'],
            r['gender'],
            r['tests'],
            r['test_count'],
            r['billed'],
            r['collected'],
            r['due'],
        ])
    headers = ['Date', 'Invoice', 'Patient', 'Patient #', 'Phone', 'Age',
               'Gender', 'Tests', 'Count', 'Billed', 'Collected', 'Due']
    total_row = ['TOTAL', '', '', '', '', '', '', '', totals['tests'],
                 totals['billed'], totals['collected'], totals['due']]
    kpis = [
        ('Referral', referral_name, None),
        ('Orders', totals['orders'], '0'),
        ('Patients', totals['patients'], '0'),
        ('Billed', totals['billed'], '#,##0.00'),
        ('Collected', totals['collected'], '#,##0.00'),
        ('Outstanding', totals['due'], '#,##0.00'),
    ]
    buf = build_workbook(
        'Doctor Detail: ' + referral_name,
        f"{d_from.strftime('%d-%b-%Y')} to {d_to.strftime('%d-%b-%Y')}",
        kpis, headers, data,
        widths=[18, 14, 22, 14, 14, 6, 8, 40, 8, 12, 12, 12],
        number_cols=[9, 10, 11, 12],
        total_row=total_row,
    )
    safe_name = ''.join(c for c in referral_name if c.isalnum() or c in ' -_')[:40]
    return send_file(buf, as_attachment=True,
        download_name=f'doctor_{safe_name}_{d_from:%Y%m%d}_{d_to:%Y%m%d}.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
'''
    with open(rp, 'w', encoding='utf-8') as f:
        f.write(r + new_route)
    print('OK  - routes.py: doctor_detail route added')
else:
    print('SKIP - routes.py already has doctor_detail')


# ---------- 3. Create doctor_detail.html ----------
import os
tpl_path = 'modules/analytics/templates/analytics/doctor_detail.html'

tpl = """{% extends 'analytics/_base.html' %}
{% block report_title %}Referral Detail: {{ referral_name }}{% endblock %}
{% block excel_url %}/analytics/doctors/{{ referral_name }}.xlsx?date_from={{ date_from_raw }}&date_to={{ date_to_raw }}{% endblock %}

{% block report_body %}
<table class="an-kpi">
  <tr>
    <td><div class="an-kpi-label">Orders</div><div class="an-kpi-value">{{ totals.orders }}</div></td>
    <td><div class="an-kpi-label">Patients</div><div class="an-kpi-value">{{ totals.patients }}</div></td>
    <td><div class="an-kpi-label">Tests</div><div class="an-kpi-value">{{ totals.tests }}</div></td>
    <td><div class="an-kpi-label">Billed</div><div class="an-kpi-value">{{ totals.billed | money }}</div></td>
    <td><div class="an-kpi-label">Collected</div><div class="an-kpi-value text-success">{{ totals.collected | money }}</div></td>
    <td><div class="an-kpi-label">Outstanding</div><div class="an-kpi-value text-danger">{{ totals.due | money }}</div></td>
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
      <th>Age</th>
      <th>Gender</th>
      <th>Tests</th>
      <th class="num">Billed</th>
      <th class="num">Collected</th>
      <th class="num">Due</th>
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
      <td class="muted">{{ r.age }}</td>
      <td class="muted">{{ r.gender }}</td>
      <td class="muted">{{ r.tests }}</td>
      <td class="num">{{ r.billed | money }}</td>
      <td class="num text-success">{{ r.collected | money }}</td>
      <td class="num text-danger">{% if r.due > 0 %}{{ r.due | money }}{% else %}—{% endif %}</td>
    </tr>
    {% else %}
    <tr><td colspan="11" class="an-empty">No orders for this referral in this date range.</td></tr>
    {% endfor %}
  </tbody>
  <tfoot>
    <tr>
      <td colspan="8">TOTAL</td>
      <td class="num">{{ totals.billed | money }}</td>
      <td class="num">{{ totals.collected | money }}</td>
      <td class="num">{{ totals.due | money }}</td>
    </tr>
  </tfoot>
</table>
{% endblock %}
"""

with open(tpl_path, 'w', encoding='utf-8') as f:
    f.write(tpl)
print('OK  - doctor_detail.html created')


# ---------- 4. Make doctor names clickable in doctors.html ----------
dp = 'modules/analytics/templates/analytics/doctors.html'
d = open(dp, encoding='utf-8').read()

old_name = "      <td class=\"fw-semibold\">{{ r.name }}</td>"
new_name = "      <td class=\"fw-semibold\"><a href=\"/analytics/doctors/{{ r.name }}\" class=\"text-decoration-none\">{{ r.name }}</a></td>"

if old_name in d and 'analytics/doctors/{{ r.name }}' not in d:
    d = d.replace(old_name, new_name, 1)
    with open(dp, 'w', encoding='utf-8') as f:
        f.write(d)
    print('OK  - doctors.html: names now clickable')
elif 'analytics/doctors/{{ r.name }}' in d:
    print('SKIP - doctors.html already has links')
else:
    print('WARN - doctors.html: name cell pattern not found')


print()
print('=' * 55)
print('Done. Restart Flask and:')
print('  1. Open /analytics/doctors')
print('  2. Click any doctor name')
print('  3. See their full patient list')
print('  4. Excel button exports the detail')
print('=' * 55)

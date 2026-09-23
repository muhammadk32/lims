# ============================================================
# Simplify commission detail table:
#   Date · Invoice · Patient · Tests (names) · Total · Discount · Share
# ============================================================
import os

# ---------- 1. Query: include test names ----------
qp = 'modules/analytics/queries.py'
q = open(qp, encoding='utf-8').read()

old_row = """        rows.append({
            'order_id': o.id,
            'order_code': o.order_code,
            'date': o.created_at,
            'patient': o.patient.full_name,
            'patient_code': o.patient.patient_code,
            'phone': o.patient.phone or '-',
            'tests': o.item_count or 0,
            'subtotal': subtotal,
            'discount': discount,
            'net': net,
            'commission_pct': pct,
            'commission': round(o.commission_amount or 0, 2),
            'commission_paid': bool(o.commission_paid),
            'commission_paid_at': o.commission_paid_at,
        })"""

new_row = """        test_names = ', '.join(
            (i.test.name if i.test else '?')
            for i in o.top_level_items
        )
        rows.append({
            'order_id': o.id,
            'order_code': o.order_code,
            'date': o.created_at,
            'patient': o.patient.full_name,
            'patient_code': o.patient.patient_code,
            'tests_list': test_names,
            'tests': o.item_count or 0,
            'total': net,
            'subtotal': subtotal,
            'discount': discount,
            'net': net,
            'commission_pct': pct,
            'commission': round(o.commission_amount or 0, 2),
            'commission_paid': bool(o.commission_paid),
            'commission_paid_at': o.commission_paid_at,
        })"""

if old_row in q:
    q = q.replace(old_row, new_row, 1)
    open(qp, 'w', encoding='utf-8').write(q)
    print('OK  - queries.py: test names added')
elif 'tests_list' in q:
    print('SKIP - queries already has tests_list')
else:
    print('WARN - row build block not found')


# ---------- 2. New template — simplified columns ----------
tpl = """{% extends 'analytics/_base.html' %}
{% block report_title %}Commission Detail: {{ referral_name }}{% endblock %}
{% block excel_url %}/analytics/commissions/{{ referral_name }}.xlsx?date_from={{ date_from_raw }}&date_to={{ date_to_raw }}{% endblock %}

{% block report_body %}

<div style="background:#f8f9fa; border:1px solid #212529; padding:8px 14px; margin-bottom:12px; font-size:0.78rem;">
  <strong>Formula:</strong>
  Commission = <strong>(Subtotal × %)</strong> − <strong>Discount</strong>
</div>

<table class="an-kpi">
  <tr>
    <td><div class="an-kpi-label">Orders</div><div class="an-kpi-value">{{ totals.orders }}</div></td>
    <td><div class="an-kpi-label">Total Billed</div><div class="an-kpi-value">{{ totals.net | money }}</div></td>
    <td><div class="an-kpi-label">Total Discount</div><div class="an-kpi-value text-danger">−{{ totals.discount | money }}</div></td>
    <td><div class="an-kpi-label">Total Share</div><div class="an-kpi-value fw-bold">{{ totals.commission | money }}</div></td>
    <td><div class="an-kpi-label">Paid</div><div class="an-kpi-value text-success">{{ totals.paid | money }}</div></td>
    <td><div class="an-kpi-label">Outstanding</div><div class="an-kpi-value text-danger">{{ totals.outstanding | money }}</div></td>
  </tr>
</table>

<table class="an-table">
  <thead>
    <tr>
      <th style="width: 110px;">Date</th>
      <th style="width: 110px;">Invoice</th>
      <th style="width: 18%;">Patient</th>
      <th>Tests</th>
      <th class="num" style="width: 100px;">Total</th>
      <th class="num" style="width: 100px;">Discount</th>
      <th class="num" style="width: 100px;">Share</th>
      <th style="width: 90px;">Status</th>
    </tr>
  </thead>
  <tbody>
    {% for r in rows %}
    <tr>
      <td class="muted">{{ r.date | localtime('%d/%m/%y %H:%M') }}</td>
      <td><a href="/orders/{{ r.order_id }}" class="text-decoration-none"><code>INV-{{ r.order_code }}</code></a></td>
      <td class="fw-semibold">{{ r.patient }}</td>
      <td class="muted" style="font-size: 0.76rem;">{{ r.tests_list }}</td>
      <td class="num">{{ r.total | money }}</td>
      <td class="num text-danger">{% if r.discount > 0 %}−{{ r.discount | money }}{% else %}—{% endif %}</td>
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
    <tr><td colspan="8" class="an-empty">No commission data for this referral in this range.</td></tr>
    {% endfor %}
  </tbody>
  <tfoot>
    <tr>
      <td colspan="4">TOTAL</td>
      <td class="num">{{ totals.net | money }}</td>
      <td class="num">−{{ totals.discount | money }}</td>
      <td class="num">{{ totals.commission | money }}</td>
      <td></td>
    </tr>
  </tfoot>
</table>
{% endblock %}
"""

open('modules/analytics/templates/analytics/commission_detail.html', 'w', encoding='utf-8').write(tpl)
print('OK  - commission_detail.html simplified')


# ---------- 3. Simplify Excel export to match ----------
rp = 'modules/analytics/routes.py'
r = open(rp, encoding='utf-8').read()

old_excel = """    data = []
    for r in rows:
        pct_amount = round(r['subtotal'] * r['commission_pct'] / 100.0, 2)
        data.append([
            r['date'].strftime('%d-%b-%Y %H:%M') if r['date'] else '',
            'INV-' + r['order_code'],
            r['patient'],
            r['patient_code'],
            r['tests'],
            r['subtotal'],
            r['commission_pct'],
            pct_amount,
            r['discount'],
            r['commission'],
            'PAID' if r['commission_paid'] else 'PENDING',
        ])
    headers = ['Date', 'Invoice', 'Patient', 'Patient #',
               'Tests', 'Subtotal', 'Pct %', 'Subtotal x %',
               'Less Discount', 'Commission', 'Status']
    total_row = ['TOTAL', '', '', '', totals['orders'],
                 totals['subtotal'], '',
                 '', totals['discount'],
                 totals['commission'], '']"""

new_excel = """    data = []
    for r in rows:
        data.append([
            r['date'].strftime('%d-%b-%Y %H:%M') if r['date'] else '',
            'INV-' + r['order_code'],
            r['patient'],
            r['tests_list'],
            r['total'],
            r['discount'],
            r['commission'],
            'PAID' if r['commission_paid'] else 'PENDING',
        ])
    headers = ['Date', 'Invoice', 'Patient', 'Tests',
               'Total', 'Discount', 'Share', 'Status']
    total_row = ['TOTAL', '', '', '',
                 totals['net'], totals['discount'],
                 totals['commission'], '']"""

if old_excel in r:
    r = r.replace(old_excel, new_excel, 1)
    r = r.replace(
        "        widths=[18, 14, 22, 14, 8, 12, 8, 14, 14, 14, 12],\n        number_cols=[5, 6, 7, 8, 9, 10],",
        "        widths=[18, 14, 24, 34, 12, 12, 12, 10],\n        number_cols=[5, 6, 7],",
        1,
    )
    open(rp, 'w', encoding='utf-8').write(r)
    print('OK  - routes.py: Excel columns simplified')
elif "'Tests',\n               'Total'" in r or "'Tests', 'Total'" in r:
    print('SKIP - Excel already simplified')
else:
    print('WARN - Excel block pattern not found')


print()
print('=' * 55)
print('Done. Restart Flask and reload /analytics/commissions/<doctor>')
print('=' * 55)

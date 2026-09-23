"""
Change commission formula to: (Subtotal x %) - Discount
"""
import os

# ============================================================
# 1. create_order in services.py — new formula
# ============================================================
sp = 'modules/orders/services.py'
s = open(sp, encoding='utf-8').read()

old = """            if _ref and (_ref.commission_percent or 0) > 0:
                order.commission_amount = round(
                    (order.final_total or 0) * (_ref.commission_percent / 100.0), 2
                )"""

new = """            if _ref and (_ref.commission_percent or 0) > 0:
                # Commission = (Subtotal x %) - Discount   (floor at 0)
                _pct = _ref.commission_percent or 0
                _sub = order.subtotal or 0
                _disc = order.discount_value or 0
                _amt = (_sub * (_pct / 100.0)) - _disc
                order.commission_amount = round(max(0.0, _amt), 2)"""

if old in s:
    s = s.replace(old, new, 1)
    open(sp, 'w', encoding='utf-8').write(s)
    print('OK  - create_order: formula updated')
elif 'Commission = (Subtotal' in s:
    print('SKIP - create_order already uses new formula')
else:
    print('WARN - create_order anchor not found')


# ============================================================
# 2. recalculate_commissions — new formula
# ============================================================
old_recalc = """        new_amount = round((o.final_total or 0) * (pct / 100.0), 2)"""
new_recalc = """        _sub = o.subtotal or 0
        _disc = o.discount_value or 0
        new_amount = round(max(0.0, (_sub * (pct / 100.0)) - _disc), 2)"""

if old_recalc in s:
    s = s.replace(old_recalc, new_recalc, 1)
    open(sp, 'w', encoding='utf-8').write(s)
    print('OK  - recalculate_commissions: formula updated')
elif '_sub * (pct / 100.0)' in s:
    print('SKIP - recalculate_commissions already uses new formula')
else:
    print('WARN - recalculate anchor not found')


# ============================================================
# 3. commission_detail query — recompute pct label from subtotal
# ============================================================
qp = 'modules/analytics/queries.py'
q = open(qp, encoding='utf-8').read()

# The detail row now computes pct relative to net. Change to show stored pct.
old_pct = """        pct = 0.0
        if net > 0:
            pct = round((o.commission_amount / net) * 100, 2)"""

new_pct = """        # Show the referral's CURRENT % (not derived from amount, since
        # the formula subtracts discount so back-calc would be misleading)
        pct = 0.0
        try:
            from modules.referrals.models import Referral as _Ref
            _name = o.referred_by_name or (o.doctor.full_name if o.doctor else None)
            if _name:
                _r = _Ref.query.filter(_Ref.name.ilike(_name)).first()
                if _r:
                    pct = float(_r.commission_percent or 0)
        except Exception:
            pass"""

if old_pct in q:
    q = q.replace(old_pct, new_pct, 1)
    open(qp, 'w', encoding='utf-8').write(q)
    print('OK  - commission_detail: pct source updated')
else:
    print('WARN - commission_detail pct block not found')


# ============================================================
# 4. Detail template — new formula note + applied column
# ============================================================
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
    <td><div class="an-kpi-label">Subtotal</div><div class="an-kpi-value">{{ totals.subtotal | money }}</div></td>
    <td><div class="an-kpi-label">Discount</div><div class="an-kpi-value text-danger">−{{ totals.discount | money }}</div></td>
    <td><div class="an-kpi-label">Net</div><div class="an-kpi-value">{{ totals.net | money }}</div></td>
    <td><div class="an-kpi-label">Commission</div><div class="an-kpi-value fw-bold">{{ totals.commission | money }}</div></td>
    <td><div class="an-kpi-label">Outstanding</div><div class="an-kpi-value text-danger">{{ totals.outstanding | money }}</div></td>
  </tr>
</table>

<table class="an-table">
  <thead>
    <tr>
      <th>Date</th>
      <th>Invoice</th>
      <th>Patient</th>
      <th class="num">Tests</th>
      <th class="num">Subtotal</th>
      <th class="num">%</th>
      <th class="num">Subtotal × %</th>
      <th class="num">Less Discount</th>
      <th class="num">Commission</th>
      <th>Status</th>
    </tr>
  </thead>
  <tbody>
    {% for r in rows %}
    {% set pct_amount = (r.subtotal * r.commission_pct / 100.0) %}
    <tr>
      <td class="muted">{{ r.date | localtime('%d/%m/%y %H:%M') }}</td>
      <td><a href="/orders/{{ r.order_id }}" class="text-decoration-none"><code>INV-{{ r.order_code }}</code></a></td>
      <td class="fw-semibold">{{ r.patient }}</td>
      <td class="num">{{ r.tests }}</td>
      <td class="num muted">{{ r.subtotal | money }}</td>
      <td class="num muted">{{ '%.2f'|format(r.commission_pct) }}%</td>
      <td class="num">{{ pct_amount | money }}</td>
      <td class="num text-danger">−{{ r.discount | money }}</td>
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
      <td colspan="4">TOTAL</td>
      <td class="num">{{ totals.subtotal | money }}</td>
      <td></td>
      <td class="num">{{ (totals.subtotal * (rows[0].commission_pct if rows else 0) / 100.0) | money }}</td>
      <td class="num">−{{ totals.discount | money }}</td>
      <td class="num">{{ totals.commission | money }}</td>
      <td></td>
    </tr>
  </tfoot>
</table>
{% endblock %}
"""

open('modules/analytics/templates/analytics/commission_detail.html', 'w', encoding='utf-8').write(tpl)
print('OK  - commission_detail.html: new formula columns added')


# ============================================================
# 5. Update Excel export columns
# ============================================================
rp = 'modules/analytics/routes.py'
r = open(rp, encoding='utf-8').read()

old_data = """    data = []
    for r in rows:
        data.append([
            r['date'].strftime('%d-%b-%Y %H:%M') if r['date'] else '',
            'INV-' + r['order_code'],
            r['patient'],
            r['patient_code'],
            r['tests'],
            r['subtotal'],
            r['discount'],
            r['net'],
            r['commission_pct'],
            r['commission'],
            'PAID' if r['commission_paid'] else 'PENDING',
        ])
    headers = ['Date', 'Invoice', 'Patient', 'Patient #',
               'Tests', 'Subtotal', 'Discount', 'Net', 'Comm %', 'Commission', 'Status']
    total_row = ['TOTAL', '', '', '', totals['orders'],
                 totals['subtotal'], totals['discount'], totals['net'],
                 '', totals['commission'], '']"""

new_data = """    data = []
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

if old_data in r:
    r = r.replace(old_data, new_data, 1)
    r = r.replace(
        "        widths=[18, 14, 22, 14, 8, 12, 12, 12, 10, 14, 12],\n        number_cols=[5, 6, 7, 8, 9, 10],",
        "        widths=[18, 14, 22, 14, 8, 12, 8, 14, 14, 14, 12],\n        number_cols=[5, 6, 7, 8, 9, 10],",
        1,
    )
    open(rp, 'w', encoding='utf-8').write(r)
    print('OK  - routes.py: Excel export updated')
else:
    print('WARN - Excel export anchor not found')


print()
print('=' * 55)
print('Done. Restart Flask, then:')
print('  1. /settings/referrals -> Recalculate (to backfill old orders)')
print('  2. /analytics/commissions -> click doctor -> see breakdown')
print()
print('New formula: Commission = (Subtotal x %) - Discount')
print('=' * 55)

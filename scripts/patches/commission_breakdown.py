"""
Commission breakdown + recalculate feature.
"""
import os

# ============================================================
# 1. Enhance commission_detail query — add subtotal + discount
# ============================================================
qp = 'modules/analytics/queries.py'
q = open(qp, encoding='utf-8').read()

if "'subtotal':" not in q.split('def commission_detail')[1][:600] if 'def commission_detail' in q else False:
    # Replace the existing commission_detail body
    old_block_start = q.find('def commission_detail(')
    if old_block_start != -1:
        # Find the end of the function (next def or EOF)
        next_def = q.find('\ndef ', old_block_start + 1)
        end = next_def if next_def != -1 else len(q)

        new_fn = '''def commission_detail(referral_name, date_from, date_to):
    """Per-order commission breakdown for one referral.

    Commission = (Subtotal - Discount) x Commission % = Final Total x %
    """
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
        subtotal = round(o.subtotal or 0, 2)
        discount = round(o.discount_value or 0, 2)
        net = round(o.final_total or 0, 2)
        pct = 0.0
        if net > 0:
            pct = round((o.commission_amount / net) * 100, 2)
        rows.append({
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
        })

    totals = {
        'orders': len(rows),
        'subtotal': round(sum(r['subtotal'] for r in rows), 2),
        'discount': round(sum(r['discount'] for r in rows), 2),
        'net': round(sum(r['net'] for r in rows), 2),
        'commission': round(sum(r['commission'] for r in rows), 2),
        'paid': round(sum(r['commission'] for r in rows if r['commission_paid']), 2),
        'outstanding': round(sum(r['commission'] for r in rows if not r['commission_paid']), 2),
    }
    return rows, totals
'''
        q = q[:old_block_start] + new_fn + (q[end+1:] if end < len(q) else '')
        open(qp, 'w', encoding='utf-8').write(q)
        print('OK  - commission_detail: subtotal + discount added')
    else:
        print('WARN - commission_detail not found')
else:
    print('SKIP - commission_detail already has subtotal')


# ============================================================
# 2. Services: recalculate_commissions (backfill)
# ============================================================
sp = 'modules/orders/services.py'
s = open(sp, encoding='utf-8').read()

if 'def recalculate_commissions' not in s:
    new_svc = '''

def recalculate_commissions(date_from=None, date_to=None):
    """Recalculate commission for existing orders.

    Uses each order's current referred_by_name and the referral's CURRENT
    commission %. Returns (updated_count, total_amount).

    If date range given, only touches orders in that range.
    """
    from modules.orders.models import Order, OrderStatus
    from modules.referrals.models import Referral
    from sqlalchemy import func as _f

    query = Order.query.filter(Order.status != OrderStatus.CANCELLED)
    if date_from:
        query = query.filter(_f.date(Order.created_at) >= date_from)
    if date_to:
        query = query.filter(_f.date(Order.created_at) <= date_to)

    orders = query.all()

    # Cache referral pcts
    pcts = {r.name.lower(): (r.commission_percent or 0) for r in Referral.query.all()}

    updated = 0
    total = 0.0
    for o in orders:
        if not o.referred_by_name:
            continue
        pct = pcts.get(o.referred_by_name.lower())
        if not pct:
            continue
        new_amount = round((o.final_total or 0) * (pct / 100.0), 2)
        if abs((o.commission_amount or 0) - new_amount) > 0.001:
            o.commission_amount = new_amount
            updated += 1
            total += new_amount

    db.session.commit()
    log_action('recalc', 'order', 0,
               f'Recalculated commission for {updated} orders — total {total:.2f}')
    return updated, round(total, 2)
'''
    open(sp, 'w', encoding='utf-8').write(s + new_svc)
    print('OK  - services.py: recalculate_commissions added')
else:
    print('SKIP - recalculate_commissions exists')


# ============================================================
# 3. Route: /settings/referrals/recalculate
# ============================================================
rp = 'modules/settings/routes.py'
r = open(rp, encoding='utf-8').read()

if 'def referrals_recalculate' not in r:
    new_route = '''

@settings_bp.route('/referrals/recalculate', methods=['POST'])
@login_required
def referrals_recalculate():
    """Backfill commission on existing orders using current referral %."""
    from datetime import datetime as _dt
    from flask import flash, redirect, url_for

    d_from_str = request.form.get('date_from', '').strip()
    d_to_str = request.form.get('date_to', '').strip()
    d_from = d_to = None
    try:
        if d_from_str:
            d_from = _dt.strptime(d_from_str, '%Y-%m-%d').date()
        if d_to_str:
            d_to = _dt.strptime(d_to_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        pass

    from modules.orders.services import recalculate_commissions
    updated, total = recalculate_commissions(d_from, d_to)
    flash(
        f'Recalculated commission for {updated} order(s). '
        f'Total commission: {total:.2f}.',
        'success',
    )
    return redirect(url_for('settings.referrals'))
'''
    open(rp, 'w', encoding='utf-8').write(r + new_route)
    print('OK  - settings/routes.py: /referrals/recalculate added')
else:
    print('SKIP - recalculate route exists')


# ============================================================
# 4. Add recalculate button to referrals page
# ============================================================
tp = 'templates/settings/referrals.html'
t = open(tp, encoding='utf-8').read()

if 'referrals_recalculate' not in t:
    anchor = '''  {# ============ NOTE ============ #}'''
    block = '''  {# ============ RECALCULATE ============ #}
  <p class="rfc-section" style="margin-top: 20px;">Recalculate Existing Orders</p>
  <form method="POST" action="{{ url_for('settings.referrals_recalculate') }}"
        class="rfc-add" style="display: flex; gap: 10px; align-items: end; flex-wrap: wrap;">
    <div class="rfc-field">
      <label>From (optional)</label>
      <input type="date" name="date_from">
    </div>
    <div class="rfc-field">
      <label>To (optional)</label>
      <input type="date" name="date_to">
    </div>
    <div class="rfc-field">
      <button type="submit" class="rfc-btn rfc-btn-primary"
              onclick="return confirm('Recalculate commission for all matching orders using the current %?\\n\\nThis will overwrite their existing commission_amount.');">
        <i class="bi bi-arrow-clockwise"></i> Recalculate
      </button>
    </div>
    <div style="flex: 1; font-size: 0.74rem; color: #6c757d;">
      Commission = <strong>(Subtotal − Discount) × Referral %</strong>.
      Applied to orders already created. Leave dates blank to recalculate ALL orders.
    </div>
  </form>

'''
    if anchor in t:
        t = t.replace(anchor, block + anchor, 1)
        open(tp, 'w', encoding='utf-8').write(t)
        print('OK  - referrals.html: recalculate form added')
    else:
        print('WARN - referrals.html anchor not found')


# ============================================================
# 5. Update commission_detail.html — show breakdown columns
# ============================================================
tpl = """{% extends 'analytics/_base.html' %}
{% block report_title %}Commission Detail: {{ referral_name }}{% endblock %}
{% block excel_url %}/analytics/commissions/{{ referral_name }}.xlsx?date_from={{ date_from_raw }}&date_to={{ date_to_raw }}{% endblock %}

{% block report_body %}

<div style="background:#f8f9fa; border:1px solid #212529; padding:8px 14px; margin-bottom:12px; font-size:0.78rem;">
  <strong>Calculation:</strong>
  Commission = <strong>(Subtotal − Discount) × Commission %</strong>
  = <strong>Final Total × %</strong>
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
      <th class="num">Discount</th>
      <th class="num">Net</th>
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
      <td class="num">{{ r.tests }}</td>
      <td class="num muted">{{ r.subtotal | money }}</td>
      <td class="num text-danger">−{{ r.discount | money }}</td>
      <td class="num">{{ r.net | money }}</td>
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
      <td colspan="4">TOTAL</td>
      <td class="num">{{ totals.subtotal | money }}</td>
      <td class="num">−{{ totals.discount | money }}</td>
      <td class="num">{{ totals.net | money }}</td>
      <td></td>
      <td class="num">{{ totals.commission | money }}</td>
      <td></td>
    </tr>
  </tfoot>
</table>
{% endblock %}
"""

open('modules/analytics/templates/analytics/commission_detail.html', 'w', encoding='utf-8').write(tpl)
print('OK  - commission_detail.html updated with breakdown')


# ============================================================
# 6. Update Excel export in routes
# ============================================================
rp2 = 'modules/analytics/routes.py'
r2 = open(rp2, encoding='utf-8').read()

old_excel = '''    data = []
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
                 '', totals['commission'], '']'''

new_excel = '''    data = []
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
                 '', totals['commission'], '']'''

if old_excel in r2:
    r2 = r2.replace(old_excel, new_excel, 1)
    # Update KPI block
    old_kpis = '''    kpis = [
        ('Referral', referral_name, None),
        ('Orders', totals['orders'], '0'),
        ('Billed', totals['billed'], '#,##0.00'),
        ('Commission', totals['commission'], '#,##0.00'),
        ('Paid', totals['paid'], '#,##0.00'),
        ('Outstanding', totals['outstanding'], '#,##0.00'),
    ]'''
    new_kpis = '''    kpis = [
        ('Referral', referral_name, None),
        ('Orders', totals['orders'], '0'),
        ('Subtotal', totals['subtotal'], '#,##0.00'),
        ('Discount', totals['discount'], '#,##0.00'),
        ('Net', totals['net'], '#,##0.00'),
        ('Commission', totals['commission'], '#,##0.00'),
        ('Outstanding', totals['outstanding'], '#,##0.00'),
    ]'''
    r2 = r2.replace(old_kpis, new_kpis, 1)
    # Update widths
    r2 = r2.replace(
        "        widths=[18, 14, 22, 14, 14, 8, 12, 10, 14, 12],\n        number_cols=[6, 7, 8, 9],",
        "        widths=[18, 14, 22, 14, 8, 12, 12, 12, 10, 14, 12],\n        number_cols=[5, 6, 7, 8, 9, 10],",
        1,
    )
    open(rp2, 'w', encoding='utf-8').write(r2)
    print('OK  - routes.py: Excel export updated with breakdown')
else:
    print('SKIP - Excel export already updated')


print()
print('=' * 55)
print('Done. Restart Flask and:')
print('  1. /analytics/commissions -> click doctor -> see breakdown')
print('  2. /settings/referrals -> new Recalculate section (top)')
print('  3. Use it to backfill old orders')
print('=' * 55)

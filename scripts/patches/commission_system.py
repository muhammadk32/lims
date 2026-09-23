"""
Commission system — percent of final total (after discount).
"""
import os

# ============================================================
# 1. Model: Referral gets commission_percent
# ============================================================
p = 'modules/referrals/models.py'
s = open(p, encoding='utf-8').read()

if 'commission_percent' not in s:
    anchor = "    # Usage counters — help rank suggestions"
    if anchor in s:
        s = s.replace(
            anchor,
            "    # Commission percent (0-100). E.g. 20.0 = 20%% of final total.\n"
            "    commission_percent = db.Column(db.Float, nullable=False, default=0.0)\n\n"
            + anchor,
            1,
        )
        open(p, 'w', encoding='utf-8').write(s)
        print('OK  - Referral model: commission_percent added')
    else:
        print('WARN - Referral anchor not found')
else:
    print('SKIP - Referral already has commission_percent')

# ============================================================
# 2. Model: Order gets commission fields
# ============================================================
p = 'modules/orders/models.py'
s = open(p, encoding='utf-8').read()

if 'commission_amount' not in s:
    anchor = "    # ---- Cancellation + auto-refund ----"
    if anchor in s:
        s = s.replace(
            anchor,
            "    # ---- Referral commission (snapshot at order creation) ----\n"
            "    commission_amount = db.Column(db.Float, nullable=False, default=0.0)\n"
            "    commission_paid = db.Column(db.Boolean, nullable=False, default=False)\n"
            "    commission_paid_at = db.Column(db.DateTime, nullable=True)\n\n"
            + anchor,
            1,
        )
        open(p, 'w', encoding='utf-8').write(s)
        print('OK  - Order model: commission fields added')
    else:
        print('WARN - Order anchor not found')
else:
    print('SKIP - Order already has commission_amount')

# ============================================================
# 3. ALTER TABLEs
# ============================================================
print()
print('Adding columns to DB...')
from app import app
from extensions import db
from sqlalchemy import text

with app.app_context():
    stmts = [
        "ALTER TABLE referrals ADD COLUMN commission_percent FLOAT DEFAULT 0.0",
        "ALTER TABLE orders ADD COLUMN commission_amount FLOAT DEFAULT 0.0",
        "ALTER TABLE orders ADD COLUMN commission_paid BOOLEAN DEFAULT 0",
        "ALTER TABLE orders ADD COLUMN commission_paid_at DATETIME",
    ]
    for stmt in stmts:
        try:
            db.session.execute(text(stmt))
            db.session.commit()
            col = stmt.split('ADD COLUMN')[1].strip().split()[0]
            print(f'  + {col}')
        except Exception as e:
            col = stmt.split('ADD COLUMN')[1].strip().split()[0]
            if 'duplicate column' in str(e).lower():
                print(f'  = {col} already exists')
            else:
                print(f'  ! {col}: {e}')

# ============================================================
# 4. create_order — compute commission
# ============================================================
p = 'modules/orders/services.py'
s = open(p, encoding='utf-8').read()

if 'commission_amount=' not in s:
    anchor = "    # ---------- Referral suggestion cache ----------"
    if anchor in s:
        block = '''    # ---------- Commission (percent of final total) ----------
    if referred_by_name:
        try:
            from modules.referrals.models import Referral as _Ref
            _ref = _Ref.query.filter(_Ref.name.ilike(referred_by_name)).first()
            if _ref and (_ref.commission_percent or 0) > 0:
                order.commission_amount = round(
                    (order.final_total or 0) * (_ref.commission_percent / 100.0), 2
                )
        except Exception as _e:
            print(f'[orders.services] commission calc failed: {_e}')

'''
        s = s.replace(anchor, block + anchor, 1)
        open(p, 'w', encoding='utf-8').write(s)
        print('OK  - create_order: commission computed')
    else:
        print('WARN - commission anchor not found in services.py')
else:
    print('SKIP - commission already in create_order')

# ============================================================
# 5. Settings page for referral commissions
# ============================================================
os.makedirs('modules/settings/templates/settings', exist_ok=True)

# --- Add routes to settings/routes.py ---
p = 'modules/settings/routes.py'
s = open(p, encoding='utf-8').read()

if 'def referrals' not in s:
    new_routes = '''

# ============================================================
# Referrals + Commission
# ============================================================
@settings_bp.route('/referrals')
@login_required
def referrals():
    """List all referrals with inline commission editor."""
    from modules.referrals.models import Referral
    from flask import request as _rq

    q_search = _rq.args.get('q', '').strip()
    query = Referral.query
    if q_search:
        query = query.filter(Referral.name.ilike(f'%{q_search}%'))
    rows = query.order_by(Referral.name.asc()).all()

    return render_template(
        'settings/referrals.html',
        rows=rows,
        q_search=q_search,
    )


@settings_bp.route('/referrals/<int:rid>/commission', methods=['POST'])
@login_required
def referral_commission(rid):
    """Update one referral's commission percent."""
    from modules.referrals.models import Referral
    from extensions import db
    from flask import request as _rq, flash, redirect, url_for

    ref = Referral.query.get_or_404(rid)
    try:
        pct = float(_rq.form.get('commission_percent', 0))
    except (ValueError, TypeError):
        pct = 0.0
    pct = max(0.0, min(100.0, pct))
    ref.commission_percent = pct
    db.session.commit()
    flash(f'Commission updated for {ref.name}: {pct:.1f}%', 'success')
    return redirect(url_for('settings.referrals'))


@settings_bp.route('/referrals/<int:rid>/delete', methods=['POST'])
@login_required
def referral_delete(rid):
    """Remove a referral suggestion (safe — orders keep their referred_by_name)."""
    from modules.referrals.models import Referral
    from extensions import db
    from flask import flash, redirect, url_for

    ref = Referral.query.get_or_404(rid)
    name = ref.name
    db.session.delete(ref)
    db.session.commit()
    flash(f'Referral "{name}" removed from suggestions.', 'info')
    return redirect(url_for('settings.referrals'))
'''
    open(p, 'w', encoding='utf-8').write(s + new_routes)
    print('OK  - settings/routes.py: referral routes added')
else:
    print('SKIP - settings already has referrals routes')

# --- Create template ---
tpl = """{% extends 'base.html' %}
{% block title %}Referrals & Commission - LabMS{% endblock %}

{% block content %}
<div class="container-fluid py-4" style="max-width: 1000px;">

  <div class="d-flex justify-content-between align-items-center mb-3">
    <div>
      <h3 class="fw-bold mb-0"><i class="bi bi-person-badge"></i> Referrals & Commission</h3>
      <p class="text-muted small mb-0">
        Set percent commission for each referring doctor. Applied as % of final total (after discount).
      </p>
    </div>
  </div>

  <form method="GET" class="row g-2 mb-3">
    <div class="col-md-6">
      <input type="text" name="q" value="{{ q_search }}" class="form-control"
             placeholder="Search referral name...">
    </div>
    <div class="col-md-2">
      <button class="btn btn-primary w-100"><i class="bi bi-search"></i> Search</button>
    </div>
    {% if q_search %}
    <div class="col-md-2">
      <a href="{{ url_for('settings.referrals') }}" class="btn btn-outline-danger w-100">
        <i class="bi bi-x-lg"></i> Clear
      </a>
    </div>
    {% endif %}
  </form>

  <div class="card border-0 shadow-sm">
    <div class="table-responsive">
      <table class="table table-hover align-middle mb-0">
        <thead class="table-light">
          <tr>
            <th>Name</th>
            <th>Clinic</th>
            <th>Phone</th>
            <th class="text-center">Times Used</th>
            <th class="text-end" style="width: 130px;">Commission %</th>
            <th class="text-end" style="width: 120px;">Action</th>
          </tr>
        </thead>
        <tbody>
          {% for r in rows %}
          <tr>
            <td class="fw-semibold">{{ r.name }}</td>
            <td class="text-muted small">{{ r.clinic or '—' }}</td>
            <td class="text-muted small">{{ r.phone or '—' }}</td>
            <td class="text-center">
              <span class="badge bg-secondary">{{ r.times_used or 0 }}</span>
            </td>
            <td class="text-end">
              <form method="POST" action="{{ url_for('settings.referral_commission', rid=r.id) }}"
                    class="d-flex justify-content-end gap-1">
                <div class="input-group input-group-sm" style="max-width: 110px;">
                  <input type="number" name="commission_percent" step="0.01" min="0" max="100"
                         value="{{ '%.2f'|format(r.commission_percent or 0) }}"
                         class="form-control text-end">
                  <span class="input-group-text">%</span>
                </div>
                <button class="btn btn-sm btn-success"><i class="bi bi-check-lg"></i></button>
              </form>
            </td>
            <td class="text-end">
              <form method="POST" action="{{ url_for('settings.referral_delete', rid=r.id) }}"
                    onsubmit="return confirm('Remove this referral from suggestions?');">
                <button class="btn btn-sm btn-outline-danger"><i class="bi bi-trash"></i></button>
              </form>
            </td>
          </tr>
          {% else %}
          <tr>
            <td colspan="6" class="text-center text-muted py-5">
              <i class="bi bi-inbox fs-3 d-block mb-2"></i>
              {% if q_search %}No matches.{% else %}No referrals yet.{% endif %}
            </td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  </div>

  <div class="text-muted small mt-3">
    <i class="bi bi-info-circle"></i>
    Commission is calculated as <strong>final total (after discount) × commission %</strong>
    and saved with each new order. Changing the % here does <strong>not</strong> affect
    past orders.
  </div>

</div>
{% endblock %}
"""
open('modules/settings/templates/settings/referrals.html', 'w', encoding='utf-8').write(tpl)
print('OK  - settings/templates/settings/referrals.html created')

# ============================================================
# 6. Analytics: Commissions report
# ============================================================
p = 'modules/analytics/queries.py'
s = open(p, encoding='utf-8').read()

if 'def commission_report' not in s:
    new_fn = '''

# ============================================================
# 6. Commission Report
# ============================================================
def commission_report(date_from, date_to):
    from modules.orders.models import Order, OrderStatus
    d_from, d_to = _parse_range(date_from, date_to)

    orders = (Order.query
        .filter(func.date(Order.created_at) >= d_from)
        .filter(func.date(Order.created_at) <= d_to)
        .filter(Order.status != OrderStatus.CANCELLED)
        .all())

    buckets = {}
    for o in orders:
        if not (o.commission_amount or 0):
            continue
        name = o.referred_by_name or (o.doctor.full_name if o.doctor else 'Walk-in')
        if name not in buckets:
            buckets[name] = {
                'name': name, 'orders': 0,
                'billed': 0.0, 'commission': 0.0,
                'paid': 0.0, 'outstanding': 0.0,
            }
        b = buckets[name]
        b['orders'] += 1
        b['billed'] += o.final_total or 0
        b['commission'] += o.commission_amount or 0
        if o.commission_paid:
            b['paid'] += o.commission_amount or 0
        else:
            b['outstanding'] += o.commission_amount or 0

    rows = sorted(buckets.values(), key=lambda r: r['commission'], reverse=True)
    for r in rows:
        for k in ('billed', 'commission', 'paid', 'outstanding'):
            r[k] = round(r[k], 2)

    totals = {
        'refs': len(rows),
        'orders': sum(r['orders'] for r in rows),
        'commission': round(sum(r['commission'] for r in rows), 2),
        'paid': round(sum(r['paid'] for r in rows), 2),
        'outstanding': round(sum(r['outstanding'] for r in rows), 2),
    }
    return rows, totals
'''
    open(p, 'w', encoding='utf-8').write(s + new_fn)
    print('OK  - analytics/queries.py: commission_report added')
else:
    print('SKIP - commission_report exists')

# --- Add route ---
p = 'modules/analytics/routes.py'
s = open(p, encoding='utf-8').read()

if 'def commissions(' not in s:
    new_route = '''

# ============================================================
# Commission Report
# ============================================================
@analytics_bp.route('/commissions')
@login_required
@permission_required('view_reports')
def commissions():
    d_from, d_to = _range_from_request()
    rows, totals = q.commission_report(d_from, d_to)
    return render_template('analytics/commissions.html',
                           **_ctx(d_from, d_to, rows=rows, totals=totals))


@analytics_bp.route('/commissions.xlsx')
@login_required
@permission_required('view_reports')
def commissions_xlsx():
    d_from, d_to = _range_from_request()
    rows, totals = q.commission_report(d_from, d_to)

    data = [[r['name'], r['orders'], r['billed'], r['commission'],
             r['paid'], r['outstanding']] for r in rows]
    headers = ['Referral', 'Orders', 'Billed', 'Commission',
               'Paid', 'Outstanding']
    total_row = ['TOTAL', totals['orders'], '', totals['commission'],
                 totals['paid'], totals['outstanding']]
    kpis = [
        ('Referrals', totals['refs'], '0'),
        ('Commission Earned', totals['commission'], '#,##0.00'),
        ('Commission Paid', totals['paid'], '#,##0.00'),
        ('Outstanding', totals['outstanding'], '#,##0.00'),
    ]
    buf = build_workbook(
        'Referral Commission Report',
        f"{d_from.strftime('%d-%b-%Y')} to {d_to.strftime('%d-%b-%Y')}",
        kpis, headers, data,
        widths=[28, 10, 14, 14, 14, 14],
        number_cols=[2, 3, 4, 5, 6],
        total_row=total_row,
    )
    return send_file(buf, as_attachment=True,
        download_name=f'commissions_{d_from:%Y%m%d}_{d_to:%Y%m%d}.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
'''
    open(p, 'w', encoding='utf-8').write(s + new_route)
    print('OK  - analytics/routes.py: commissions route added')
else:
    print('SKIP - commissions route exists')

# --- Create commissions.html ---
tpl = """{% extends 'analytics/_base.html' %}
{% block report_title %}Referral Commission Report{% endblock %}
{% block excel_url %}{{ url_for('analytics.commissions_xlsx', date_from=date_from_raw, date_to=date_to_raw) }}{% endblock %}

{% block report_body %}
<table class="an-kpi">
  <tr>
    <td><div class="an-kpi-label">Referrals</div><div class="an-kpi-value">{{ totals.refs }}</div></td>
    <td><div class="an-kpi-label">Orders</div><div class="an-kpi-value">{{ totals.orders }}</div></td>
    <td><div class="an-kpi-label">Commission Earned</div><div class="an-kpi-value">{{ totals.commission | money }}</div></td>
    <td><div class="an-kpi-label">Paid</div><div class="an-kpi-value text-success">{{ totals.paid | money }}</div></td>
    <td><div class="an-kpi-label">Outstanding</div><div class="an-kpi-value text-danger">{{ totals.outstanding | money }}</div></td>
  </tr>
</table>

<table class="an-table">
  <thead>
    <tr>
      <th>Referral</th>
      <th class="num">Orders</th>
      <th class="num">Billed</th>
      <th class="num">Commission</th>
      <th class="num">Paid</th>
      <th class="num">Outstanding</th>
    </tr>
  </thead>
  <tbody>
    {% for r in rows %}
    <tr>
      <td class="fw-semibold">{{ r.name }}</td>
      <td class="num">{{ r.orders }}</td>
      <td class="num">{{ r.billed | money }}</td>
      <td class="num fw-semibold">{{ r.commission | money }}</td>
      <td class="num text-success">{{ r.paid | money }}</td>
      <td class="num text-danger">{{ r.outstanding | money }}</td>
    </tr>
    {% else %}
    <tr><td colspan="6" class="an-empty">
      No commission data in this range.
      Set commission % in <a href="/settings/referrals">Settings &rarr; Referrals</a>.
    </td></tr>
    {% endfor %}
  </tbody>
  <tfoot>
    <tr>
      <td>TOTAL</td>
      <td class="num">{{ totals.orders }}</td>
      <td></td>
      <td class="num">{{ totals.commission | money }}</td>
      <td class="num">{{ totals.paid | money }}</td>
      <td class="num">{{ totals.outstanding | money }}</td>
    </tr>
  </tfoot>
</table>
{% endblock %}
"""
open('modules/analytics/templates/analytics/commissions.html', 'w', encoding='utf-8').write(tpl)
print('OK  - analytics/templates/analytics/commissions.html created')

# ============================================================
# 7. Add commission card to analytics hub
# ============================================================
p = 'modules/analytics/templates/analytics/index.html'
s = open(p, encoding='utf-8').read()

if 'analytics.commissions' not in s:
    anchor = '''    <a class="rh-card" href="{{ url_for('analytics.daily') }}">'''
    card = '''    <a class="rh-card" href="{{ url_for('analytics.commissions') }}">
      <span class="icon text-warning"><i class="bi bi-cash-stack"></i></span>
      <div class="name">Referral Commissions</div>
      <div class="desc">Earned, paid, and outstanding commission per referring doctor.</div>
    </a>

'''
    if anchor in s:
        s = s.replace(anchor, card + anchor, 1)
        open(p, 'w', encoding='utf-8').write(s)
        print('OK  - analytics hub: commission card added')
    else:
        print('WARN - analytics hub anchor not found')

print()
print('=' * 55)
print('Done. Restart Flask and test:')
print('  1. /settings/referrals -> set commission % per doctor')
print('  2. Create a new order with that referral')
print('  3. /analytics/commissions -> see the report')
print('=' * 55)

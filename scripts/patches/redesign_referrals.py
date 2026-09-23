"""
Referrals page redesign:
- Dense classical layout matching analytics reports
- Add new referral form (name + clinic + phone + commission %)
- Delete with confirm
- Wider columns, inline commission editor
"""
import os

# ============================================================
# 1. Add POST route: /settings/referrals/create
# ============================================================
rp = 'modules/settings/routes.py'
r = open(rp, encoding='utf-8').read()

if 'def referral_create' not in r:
    new_route = '''

@settings_bp.route('/referrals/create', methods=['POST'])
@login_required
def referral_create():
    """Add a new referral. Available in the registration typeahead immediately."""
    from modules.referrals.models import Referral
    from extensions import db
    from flask import request as _rq, flash, redirect, url_for
    from sqlalchemy import func

    name = (_rq.form.get('name') or '').strip()
    clinic = (_rq.form.get('clinic') or '').strip()
    phone = (_rq.form.get('phone') or '').strip()
    try:
        pct = float(_rq.form.get('commission_percent', 0) or 0)
    except (ValueError, TypeError):
        pct = 0.0
    pct = max(0.0, min(100.0, pct))

    if not name:
        flash('Referral name is required.', 'warning')
        return redirect(url_for('settings.referrals'))

    existing = Referral.query.filter(
        func.lower(Referral.name) == name.lower()
    ).first()
    if existing:
        flash(f'Referral "{name}" already exists.', 'warning')
        return redirect(url_for('settings.referrals'))

    ref = Referral(
        name=name,
        clinic=clinic or None,
        phone=phone or None,
        times_used=0,
        commission_percent=pct,
    )
    db.session.add(ref)
    db.session.commit()
    flash(f'Referral "{name}" added. It will appear in the registration form.', 'success')
    return redirect(url_for('settings.referrals'))
'''
    open(rp, 'w', encoding='utf-8').write(r + new_route)
    print('OK  - settings/routes.py: /referrals/create added')
else:
    print('SKIP - /referrals/create already exists')


# ============================================================
# 2. Replace the template with the dense classical version
# ============================================================
tpl = """{% extends 'base.html' %}
{% block title %}Referrals & Commission - LabMS{% endblock %}

{% block head %}
<style>
/* ============================================================
   Referrals & Commission - dense classical layout
   ============================================================ */
.rfc-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 16px 24px 40px;
  font-family: 'Segoe UI', Arial, sans-serif;
  font-size: 0.82rem;
  color: #212529;
}

/* Header */
.rfc-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  border-bottom: 2px solid #212529;
  padding-bottom: 8px;
  margin-bottom: 14px;
  flex-wrap: wrap;
  gap: 8px;
}
.rfc-title {
  font-size: 1.15rem;
  font-weight: 700;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}
.rfc-subtitle {
  font-size: 0.76rem;
  color: #6c757d;
  margin-top: 2px;
}

/* Section heading */
.rfc-section {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #6c757d;
  margin: 0 0 8px 0;
  padding-bottom: 4px;
  border-bottom: 1px solid #dee2e6;
}

/* Add referral form */
.rfc-add {
  background: #f8f9fa;
  border: 1px solid #212529;
  padding: 12px 14px;
  margin-bottom: 18px;
}
.rfc-add-row {
  display: grid;
  grid-template-columns: 2fr 2fr 1.5fr 1fr auto;
  gap: 10px;
  align-items: end;
}
.rfc-field label {
  display: block;
  font-size: 0.64rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #6c757d;
  margin-bottom: 3px;
}
.rfc-field input {
  width: 100%;
  padding: 6px 9px;
  border: 1px solid #6c757d;
  border-radius: 0;
  font-size: 0.85rem;
  background: #fff;
}
.rfc-field input:focus {
  outline: none;
  border-color: #198754;
  box-shadow: 0 0 0 2px rgba(25, 135, 84, 0.15);
}
.rfc-field input[type="number"] {
  font-family: Consolas, Monaco, monospace;
  text-align: right;
}

/* Buttons */
.rfc-btn {
  display: inline-block;
  padding: 6px 14px;
  font-size: 0.78rem;
  font-weight: 600;
  border: 1px solid #212529;
  background: #fff;
  color: #212529;
  text-decoration: none;
  border-radius: 0;
  cursor: pointer;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  white-space: nowrap;
}
.rfc-btn:hover { background: #f1f3f5; color: #212529; }
.rfc-btn-primary {
  background: #198754;
  border-color: #198754;
  color: #fff;
}
.rfc-btn-primary:hover { background: #146c43; color: #fff; }
.rfc-btn-icon {
  padding: 5px 9px;
  font-size: 0.85rem;
}
.rfc-btn-danger {
  background: #fff;
  color: #dc3545;
  border-color: #dc3545;
}
.rfc-btn-danger:hover {
  background: #dc3545;
  color: #fff;
}

/* Search bar */
.rfc-search {
  display: flex;
  gap: 6px;
  margin-bottom: 12px;
  max-width: 500px;
}
.rfc-search input {
  flex: 1;
  padding: 6px 10px;
  border: 1px solid #6c757d;
  border-radius: 0;
  font-size: 0.85rem;
}

/* Table */
.rfc-table {
  width: 100%;
  border-collapse: collapse;
  border: 1.5px solid #212529;
  font-size: 0.82rem;
}
.rfc-table thead th {
  background: #212529;
  color: #fff;
  font-size: 0.66rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 8px 12px;
  text-align: left;
  border: 1px solid #212529;
  white-space: nowrap;
}
.rfc-table thead th.num { text-align: right; }
.rfc-table thead th.center { text-align: center; }
.rfc-table tbody td {
  padding: 8px 12px;
  border: 1px solid #6c757d;
  vertical-align: middle;
}
.rfc-table tbody tr:nth-child(even) { background: #fbfcfd; }
.rfc-table tbody tr:hover { background: #f1f3f5; }
.rfc-table .name { font-weight: 700; font-size: 0.88rem; }
.rfc-table .muted { color: #6c757d; font-size: 0.78rem; }
.rfc-table td.num {
  text-align: right;
  font-family: Consolas, Monaco, monospace;
  font-variant-numeric: tabular-nums;
}
.rfc-table td.center { text-align: center; }

/* Inline commission editor */
.rfc-comm-form {
  display: inline-flex;
  gap: 4px;
  align-items: stretch;
  justify-content: flex-end;
}
.rfc-comm-input {
  width: 82px;
  padding: 4px 8px;
  border: 1px solid #6c757d;
  border-radius: 0;
  font-size: 0.82rem;
  font-family: Consolas, Monaco, monospace;
  text-align: right;
  background: #fff;
}
.rfc-comm-pct {
  display: inline-flex;
  align-items: center;
  padding: 0 8px;
  background: #f1f3f5;
  border: 1px solid #6c757d;
  border-left: none;
  font-size: 0.78rem;
  color: #6c757d;
  font-weight: 600;
}
.rfc-save {
  padding: 4px 10px;
  background: #198754;
  color: #fff;
  border: 1px solid #198754;
  cursor: pointer;
  font-size: 0.82rem;
  border-radius: 0;
}
.rfc-save:hover { background: #146c43; }

.rfc-delete {
  padding: 4px 10px;
  background: #fff;
  color: #dc3545;
  border: 1px solid #dc3545;
  cursor: pointer;
  font-size: 0.82rem;
  border-radius: 0;
}
.rfc-delete:hover { background: #dc3545; color: #fff; }

/* Empty state */
.rfc-empty {
  text-align: center;
  padding: 40px 20px;
  color: #6c757d;
  font-style: italic;
  border: 1.5px solid #212529;
  background: #fafbfc;
}

/* Footer note */
.rfc-note {
  margin-top: 14px;
  padding-top: 10px;
  border-top: 1px solid #dee2e6;
  font-size: 0.75rem;
  color: #6c757d;
  line-height: 1.55;
}
.rfc-note strong { color: #212529; }

@media (max-width: 900px) {
  .rfc-add-row { grid-template-columns: 1fr; }
  .rfc-table { font-size: 0.74rem; }
  .rfc-table thead th,
  .rfc-table tbody td { padding: 5px 7px; }
}
</style>
{% endblock %}

{% block content %}
<div class="rfc-page">

  {# ============ HEADER ============ #}
  <div class="rfc-header">
    <div>
      <h1 class="rfc-title">
        <i class="bi bi-person-badge"></i> Referrals &amp; Commission
      </h1>
      <div class="rfc-subtitle">
        Add / edit referring doctors. Commission = % of final total (after discount).
        New referrals appear immediately in the registration form.
      </div>
    </div>
  </div>

  {# ============ ADD REFERRAL ============ #}
  <p class="rfc-section">Add New Referral</p>
  <form method="POST" action="{{ url_for('settings.referral_create') }}" class="rfc-add">
    <div class="rfc-add-row">
      <div class="rfc-field">
        <label>Name <span class="text-danger">*</span></label>
        <input type="text" name="name" required maxlength="120"
               placeholder="e.g. Dr. John Smith">
      </div>
      <div class="rfc-field">
        <label>Clinic / Hospital</label>
        <input type="text" name="clinic" maxlength="120"
               placeholder="Optional">
      </div>
      <div class="rfc-field">
        <label>Phone</label>
        <input type="tel" name="phone" maxlength="30"
               placeholder="Optional">
      </div>
      <div class="rfc-field">
        <label>Commission %</label>
        <input type="number" name="commission_percent"
               step="0.01" min="0" max="100" value="0">
      </div>
      <div class="rfc-field">
        <button type="submit" class="rfc-btn rfc-btn-primary">
          <i class="bi bi-plus-lg"></i> Add
        </button>
      </div>
    </div>
  </form>

  {# ============ SEARCH ============ #}
  <p class="rfc-section">All Referrals ({{ rows|length }})</p>
  <form method="GET" class="rfc-search">
    <input type="text" name="q" value="{{ q_search }}"
           placeholder="Search referral name...">
    <button type="submit" class="rfc-btn">
      <i class="bi bi-search"></i> Search
    </button>
    {% if q_search %}
    <a href="{{ url_for('settings.referrals') }}" class="rfc-btn rfc-btn-danger">
      <i class="bi bi-x-lg"></i> Clear
    </a>
    {% endif %}
  </form>

  {# ============ TABLE ============ #}
  {% if rows %}
  <table class="rfc-table">
    <thead>
      <tr>
        <th style="width: 26%;">Name</th>
        <th style="width: 20%;">Clinic</th>
        <th style="width: 14%;">Phone</th>
        <th class="center" style="width: 8%;">Times Used</th>
        <th class="num" style="width: 12%;">Last Used</th>
        <th class="num" style="width: 15%;">Commission %</th>
        <th class="center" style="width: 5%;">Del</th>
      </tr>
    </thead>
    <tbody>
      {% for r in rows %}
      <tr>
        <td class="name">{{ r.name }}</td>
        <td class="muted">{{ r.clinic or '—' }}</td>
        <td class="muted">{{ r.phone or '—' }}</td>
        <td class="center">
          {% if r.times_used %}
            <span class="badge bg-secondary" style="font-size:0.7rem;">{{ r.times_used }}</span>
          {% else %}
            <span class="muted">0</span>
          {% endif %}
        </td>
        <td class="num muted" style="font-size:0.72rem;">
          {% if r.last_used_at %}
            {{ r.last_used_at | localtime('%d/%m/%y') }}
          {% else %}
            —
          {% endif %}
        </td>
        <td class="num">
          <form method="POST"
                action="{{ url_for('settings.referral_commission', rid=r.id) }}"
                class="rfc-comm-form">
            <input type="number" name="commission_percent"
                   step="0.01" min="0" max="100"
                   value="{{ '%.2f'|format(r.commission_percent or 0) }}"
                   class="rfc-comm-input">
            <span class="rfc-comm-pct">%</span>
            <button type="submit" class="rfc-save" title="Save commission">
              <i class="bi bi-check-lg"></i>
            </button>
          </form>
        </td>
        <td class="center">
          <form method="POST"
                action="{{ url_for('settings.referral_delete', rid=r.id) }}"
                onsubmit="return confirm('Remove &quot;{{ r.name }}&quot; from suggestions?\n\nExisting orders keep their referral name.');">
            <button type="submit" class="rfc-delete" title="Delete">
              <i class="bi bi-trash"></i>
            </button>
          </form>
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  {% else %}
  <div class="rfc-empty">
    <i class="bi bi-inbox fs-3 d-block mb-2"></i>
    {% if q_search %}
      No referrals match "{{ q_search }}".
    {% else %}
      No referrals yet. Add the first one above.
    {% endif %}
  </div>
  {% endif %}

  {# ============ NOTE ============ #}
  <div class="rfc-note">
    <i class="bi bi-info-circle"></i>
    <strong>How it works:</strong>
    Commission is calculated as <strong>final total (after discount) × commission %</strong>
    and stored with each new order at creation time.
    Changing the % here does <strong>not</strong> affect orders already created.
    Adding a referral here makes it immediately available in the
    <em>Referred by</em> field on the registration form.
  </div>

</div>
{% endblock %}
"""

path = 'templates/settings/referrals.html'
os.makedirs('templates/settings', exist_ok=True)
with open(path, 'w', encoding='utf-8') as f:
    f.write(tpl)
print('OK  - templates/settings/referrals.html rewritten (dense classical)')

print()
print('=' * 55)
print('Done. Restart Flask and open /settings/referrals')
print('=' * 55)

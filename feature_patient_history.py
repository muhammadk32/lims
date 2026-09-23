"""
Feature 1: Patient History by Phone
- New page: /patients/history
- Search by phone, name, or code
- Table of every visit with actions per row:
    View / Revisit / Print Bill / Print Report
- "Revisit" opens /orders/new with patient + last order pre-filled (ready for Feature 2)
"""
import os

# ============================================================
# 1. Query helpers
# ============================================================
qp = 'modules/patients/queries.py'
if not os.path.exists(qp):
    open(qp, 'w', encoding='utf-8').write('"""Patient queries."""\n')

q = open(qp, encoding='utf-8').read()

if 'def search_patients_with_visits' not in q:
    q += '''

# ============================================================
# Search patients + their visit history
# ============================================================
def search_patients_with_visits(q='', limit=50):
    """Return (patients, visits_by_patient_id).

    Searches by phone, name, or patient_code.
    Each patient's visits include: order, tests, totals, status.
    """
    from modules.patients.models import Patient
    from modules.orders.models import Order, OrderStatus

    query = Patient.query

    if q:
        like = f'%{q}%'
        from sqlalchemy import or_
        query = query.filter(or_(
            Patient.phone.ilike(like),
            Patient.full_name.ilike(like),
            Patient.patient_code.ilike(like),
        ))

    patients = query.order_by(Patient.id.desc()).limit(limit).all()

    visits = {}
    for p in patients:
        orders = (
            Order.query
            .filter(Order.patient_id == p.id)
            .order_by(Order.id.desc())
            .all()
        )
        visits[p.id] = orders

    return patients, visits
'''
    open(qp, 'w', encoding='utf-8').write(q)
    print('OK  - patients/queries.py: search_patients_with_visits added')
else:
    print('SKIP - search function already exists')


# ============================================================
# 2. Route
# ============================================================
rp = 'modules/patients/routes.py'
r = open(rp, encoding='utf-8').read()

if 'def history_by_phone' not in r:
    new_route = '''

# ============================================================
# Patient History by Phone / Name / Code
# ============================================================
@patients_bp.route('/history')
@login_required
def history_by_phone():
    """Search patients and show all their visits."""
    from . import queries as pq

    q = request.args.get('q', '').strip()
    patients, visits = pq.search_patients_with_visits(q=q) if q else ([], {})

    return render_template(
        'patients/history.html',
        q=q,
        patients=patients,
        visits=visits,
    )
'''
    open(rp, 'w', encoding='utf-8').write(r + new_route)
    print('OK  - patients/routes.py: /history route added')
else:
    print('SKIP - route already exists')


# ============================================================
# 3. Template — dense classical
# ============================================================
os.makedirs('modules/patients/templates/patients', exist_ok=True)
tpl = """{% extends 'base.html' %}
{% block title %}Patient History - LabMS{% endblock %}

{% block head %}
<style>
.ph-page {
  max-width: 1500px;
  margin: 0 auto;
  padding: 10px 20px 30px;
  font-family: 'Segoe UI', Arial, sans-serif;
  font-size: 0.82rem;
  color: #212529;
}
.ph-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  border-bottom: 2px solid #212529;
  padding-bottom: 5px;
  margin-bottom: 10px;
  flex-wrap: wrap;
  gap: 8px;
}
.ph-title {
  font-size: 1.15rem;
  font-weight: 700;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}
.ph-subtitle { font-size: 0.76rem; color: #6c757d; margin-top: 2px; }
.ph-count {
  font-size: 0.76rem;
  color: #6c757d;
  font-family: Consolas, Monaco, monospace;
}

/* Search strip */
.ph-search {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  padding: 10px 12px;
  margin-bottom: 10px;
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
  align-items: end;
}
.ph-search label {
  display: block;
  font-size: 0.62rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #6c757d;
  margin-bottom: 2px;
}
.ph-search input {
  width: 100%;
  padding: 4px 10px;
  border: 1px solid #6c757d;
  border-radius: 0;
  font-size: 0.88rem;
  background: #fff;
  height: 32px;
}
.ph-search input:focus { outline: none; border-color: #198754; }

.ph-btn {
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
  height: 32px;
}
.ph-btn:hover { background: #f1f3f5; color: #212529; }
.ph-btn-primary { background: #198754; border-color: #198754; color: #fff; }
.ph-btn-primary:hover { background: #146c43; color: #fff; }

/* Patient card */
.ph-card {
  border: 1.5px solid #212529;
  margin-bottom: 14px;
  background: #fff;
}
.ph-card-header {
  background: #212529;
  color: #fff;
  padding: 6px 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
}
.ph-card-header .pname {
  font-weight: 700;
  font-size: 0.9rem;
}
.ph-card-header .pmeta {
  font-size: 0.74rem;
  font-family: Consolas, Monaco, monospace;
  opacity: 0.85;
}
.ph-card-header .pcount {
  font-size: 0.7rem;
  background: rgba(255,255,255,0.15);
  padding: 2px 8px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

/* Visits table */
.ph-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.78rem;
}
.ph-table thead th {
  background: #e9ecef;
  color: #212529;
  font-size: 0.62rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 4px 8px;
  text-align: left;
  border: 1px solid #adb5bd;
  white-space: nowrap;
}
.ph-table thead th.end { text-align: right; }
.ph-table thead th.center { text-align: center; }
.ph-table tbody td {
  padding: 4px 8px;
  border: 1px solid #dee2e6;
  vertical-align: middle;
}
.ph-table tbody tr:nth-child(even) { background: #fbfcfd; }
.ph-table tbody tr:hover { background: #f1f3f5; }
.ph-table code {
  font-size: 0.72rem;
  font-family: Consolas, Monaco, monospace;
  padding: 0 3px;
}
.ph-table .num {
  text-align: right;
  font-family: Consolas, Monaco, monospace;
  font-variant-numeric: tabular-nums;
}
.ph-table .center { text-align: center; }
.ph-table .muted { color: #6c757d; font-size: 0.72rem; }
.ph-table .tests {
  font-size: 0.74rem;
  color: #495057;
  max-width: 300px;
}
.ph-table .strike { text-decoration: line-through; color: #adb5bd !important; }

/* Badges */
.ph-badge {
  display: inline-block;
  padding: 1px 6px;
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.03em;
  border-radius: 0;
  text-transform: uppercase;
  color: #fff;
  white-space: nowrap;
}
.ph-badge-pending { background: #ffc107; color: #664d03; }
.ph-badge-collected { background: #0dcaf0; color: #055160; }
.ph-badge-completed { background: #0dcaf0; color: #055160; }
.ph-badge-approved { background: #198754; }
.ph-badge-correction { background: #ffc107; color: #664d03; }
.ph-badge-cancelled { background: #6c757d; }

/* Row action buttons */
.ph-row-actions {
  display: inline-flex;
  gap: 3px;
  flex-wrap: nowrap;
}
.ph-icon-btn {
  display: inline-block;
  padding: 2px 7px;
  font-size: 0.7rem;
  border: 1px solid #6c757d;
  background: #fff;
  color: #212529;
  text-decoration: none;
  border-radius: 0;
  cursor: pointer;
  line-height: 1.3;
  font-weight: 500;
  white-space: nowrap;
}
.ph-icon-btn:hover { background: #f1f3f5; color: #212529; }
.ph-icon-btn-revisit {
  background: #0d6efd;
  border-color: #0d6efd;
  color: #fff;
  font-weight: 600;
}
.ph-icon-btn-revisit:hover { background: #0b5ed7; color: #fff; }
.ph-icon-btn-report {
  background: #fff;
  border-color: #198754;
  color: #198754;
}
.ph-icon-btn-report:hover { background: #198754; color: #fff; }

/* Empty */
.ph-empty {
  text-align: center;
  padding: 40px 20px;
  color: #6c757d;
  font-style: italic;
  border: 1.5px solid #212529;
  background: #fafbfc;
}

@media (max-width: 900px) {
  .ph-search { grid-template-columns: 1fr; }
  .ph-table { font-size: 0.72rem; }
  .ph-table thead th,
  .ph-table tbody td { padding: 3px 5px; }
  .ph-table .tests { max-width: 150px; }
}
</style>
{% endblock %}

{% block content %}
<div class="ph-page">

  <div class="ph-header">
    <div>
      <h1 class="ph-title"><i class="bi bi-people"></i> Patient History</h1>
      <div class="ph-subtitle">Search by phone, name, or patient code to see all visits</div>
    </div>
    {% if q %}
    <div class="ph-count">
      {{ patients|length }} patient{{ 's' if patients|length != 1 }} ·
      {{ visits.values()|map('length')|sum }} visit{{ 's' if visits.values()|map('length')|sum != 1 }}
    </div>
    {% endif %}
  </div>

  {# Search #}
  <form method="GET" class="ph-search">
    <div>
      <label>Search</label>
      <input type="text" name="q" value="{{ q }}" autofocus
             placeholder="Phone / name / patient code (start typing)">
    </div>
    <button type="submit" class="ph-btn ph-btn-primary">
      <i class="bi bi-search"></i> Search
    </button>
  </form>

  {# Results #}
  {% if not q %}
  <div class="ph-empty">
    <i class="bi bi-search fs-3 d-block mb-2"></i>
    Enter a phone number, patient name, or patient code to view their visit history.
  </div>
  {% elif not patients %}
  <div class="ph-empty">
    <i class="bi bi-inbox fs-3 d-block mb-2"></i>
    No patients match "{{ q }}".
  </div>
  {% else %}

    {% for p in patients %}
    {% set patient_visits = visits.get(p.id, []) %}
    <div class="ph-card">

      <div class="ph-card-header">
        <div>
          <span class="pname">{{ p.full_name }}</span>
          <span class="pmeta">
            · {{ p.patient_code }}
            · {{ p.phone or 'no phone' }}
            {% if p.compute_age() %} · {{ p.compute_age() }}y{% endif %}
            {% if p.gender %} · {{ p.gender }}{% endif %}
          </span>
        </div>
        <span class="pcount">
          {{ patient_visits|length }} visit{{ 's' if patient_visits|length != 1 }}
        </span>
      </div>

      {% if patient_visits %}
      <table class="ph-table">
        <thead>
          <tr>
            <th style="width: 130px;">Date</th>
            <th style="width: 100px;">Lab #</th>
            <th>Tests</th>
            <th class="center" style="width: 60px;">Items</th>
            <th class="end" style="width: 80px;">Total</th>
            <th class="end" style="width: 80px;">Paid</th>
            <th class="end" style="width: 80px;">Due</th>
            <th class="center" style="width: 90px;">Status</th>
            <th class="center" style="width: 290px;">Actions</th>
          </tr>
        </thead>
        <tbody>
          {% for o in patient_visits %}
          <tr>
            <td class="muted" style="font-family: Consolas, Monaco, monospace; font-size: 0.72rem;">
              {{ o.created_at | localtime('%d/%m/%y %H:%M') }}
            </td>
            <td><code>{{ o.order_code }}</code></td>
            <td class="tests">
              {%- for item in o.top_level_items -%}
                {{ item.test.name if item.test else '?' }}{% if not loop.last %}, {% endif %}
              {%- endfor -%}
            </td>
            <td class="center">{{ o.item_count }}</td>
            <td class="num {% if o.status == 'cancelled' %}strike{% endif %}">{{ o.final_total | money }}</td>
            <td class="num">{{ o.paid_amount | money }}</td>
            <td class="num">
              {% if o.status == 'cancelled' %}—
              {% elif o.balance_due > 0.01 %}<span style="color:#b02a37; font-weight:700;">{{ o.balance_due | money }}</span>
              {% else %}—{% endif %}
            </td>
            <td class="center">
              {% set st = o.status|lower %}
              {% if st == 'pending' %}<span class="ph-badge ph-badge-pending">Pending</span>
              {% elif st == 'collected' %}<span class="ph-badge ph-badge-collected">Collected</span>
              {% elif st == 'completed' %}<span class="ph-badge ph-badge-completed">Completed</span>
              {% elif st == 'approved' %}<span class="ph-badge ph-badge-approved">Approved</span>
              {% elif st == 'correction' %}<span class="ph-badge ph-badge-correction">Correction</span>
              {% elif st == 'cancelled' %}<span class="ph-badge ph-badge-cancelled">Cancelled</span>
              {% else %}<span class="ph-badge" style="background:#e9ecef;color:#495057;">{{ o.status }}</span>
              {% endif %}
            </td>
            <td class="center">
              <div class="ph-row-actions">
                <a href="{{ url_for('orders.view_order', order_id=o.id) }}"
                   class="ph-icon-btn" title="View">
                  <i class="bi bi-eye"></i> View
                </a>
                <a href="{{ url_for('orders.new_order', patient_id=o.patient_id, revisit_from=o.id) }}"
                   class="ph-icon-btn ph-icon-btn-revisit" title="Revisit - register same patient with same tests">
                  <i class="bi bi-arrow-repeat"></i> Revisit
                </a>
                <a href="{{ url_for('orders.print_order', order_id=o.id, copy='patient') }}"
                   target="_blank" rel="noopener"
                   class="ph-icon-btn" title="Print Bill">
                  <i class="bi bi-receipt"></i> Bill
                </a>
                {% if o.status == 'approved' and o.balance_due <= 0.01 %}
                <a href="{{ url_for('reports.view_pdf', order_id=o.id) }}"
                   target="_blank" rel="noopener"
                   class="ph-icon-btn ph-icon-btn-report" title="View Report">
                  <i class="bi bi-file-earmark-medical"></i> Report
                </a>
                {% endif %}
              </div>
            </td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
      {% else %}
      <div style="padding: 14px; text-align: center; color: #6c757d; font-style: italic;">
        No visits recorded yet.
      </div>
      {% endif %}

    </div>
    {% endfor %}

  {% endif %}

</div>
{% endblock %}
"""

open('modules/patients/templates/patients/history.html', 'w', encoding='utf-8').write(tpl)
print('OK  - patients/history.html created')


# ============================================================
# 4. Add nav link in Reports dropdown (a good place)
# ============================================================
tp = 'templates/layout/topnav.html'
t = open(tp, encoding='utf-8').read()

if 'patients.history_by_phone' not in t:
    # Insert as first item in Reports dropdown (Financial section)
    anchor = '''        <div class="dropdown-section">Financial</div>'''
    insert = '''        <a href="{{ url_for('patients.history_by_phone') }}"
           class="dropdown-item {% if request.endpoint == 'patients.history_by_phone' %}active{% endif %}">
          <i class="bi bi-people"></i> Patient History
        </a>

'''
    if anchor in t:
        # Insert BEFORE the Financial section (top-level of Reports menu)
        t = t.replace(anchor, insert + anchor, 1)
        open(tp, 'w', encoding='utf-8').write(t)
        print('OK  - topnav: Patient History link added to Reports dropdown')
    else:
        print('WARN - Reports dropdown anchor not found')
else:
    print('SKIP - nav link already exists')


print()
print('=' * 55)
print('Done. Restart Flask and open:')
print('  /patients/history')
print('  Or use Reports menu -> Patient History')
print('=' * 55)

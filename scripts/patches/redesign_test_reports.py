# Rename Reports page to "Test Reports" + dense classical layout
p = 'modules/reports/templates/reports/list.html'
s = open(p, encoding='utf-8').read()

# Replace the entire template
new = """{% extends 'base.html' %}
{% block title %}Test Reports - LabMS{% endblock %}

{% block head %}
<style>
/* ============================================================
   Test Reports - dense classical layout
   ============================================================ */
.tr-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 16px 24px 40px;
  font-family: 'Segoe UI', Arial, sans-serif;
  font-size: 0.82rem;
  color: #212529;
}

/* Header */
.tr-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  border-bottom: 2px solid #212529;
  padding-bottom: 8px;
  margin-bottom: 14px;
  flex-wrap: wrap;
  gap: 8px;
}
.tr-title {
  font-size: 1.15rem;
  font-weight: 700;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}
.tr-subtitle {
  font-size: 0.76rem;
  color: #6c757d;
  margin-top: 2px;
}
.tr-count {
  font-size: 0.76rem;
  color: #6c757d;
  font-family: Consolas, Monaco, monospace;
}

/* Filters */
.tr-filter {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  padding: 10px 12px;
  margin-bottom: 12px;
  display: grid;
  grid-template-columns: 2fr 1fr auto;
  gap: 10px;
  align-items: end;
}
.tr-field label {
  display: block;
  font-size: 0.64rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #6c757d;
  margin-bottom: 3px;
}
.tr-field input,
.tr-field select {
  width: 100%;
  padding: 6px 9px;
  border: 1px solid #6c757d;
  border-radius: 0;
  font-size: 0.85rem;
  background: #fff;
}
.tr-field input:focus,
.tr-field select:focus {
  outline: none;
  border-color: #198754;
}

/* Buttons */
.tr-btn {
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
}
.tr-btn:hover { background: #f1f3f5; color: #212529; }
.tr-btn-primary { background: #198754; border-color: #198754; color: #fff; }
.tr-btn-primary:hover { background: #146c43; color: #fff; }

/* Table */
.tr-table {
  width: 100%;
  border-collapse: collapse;
  border: 1.5px solid #212529;
  font-size: 0.82rem;
}
.tr-table thead th {
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
.tr-table thead th.center { text-align: center; }
.tr-table thead th.end { text-align: right; }
.tr-table tbody td {
  padding: 8px 12px;
  border: 1px solid #6c757d;
  vertical-align: middle;
}
.tr-table tbody tr:nth-child(even) { background: #fbfcfd; }
.tr-table tbody tr:hover { background: #f1f3f5; }
.tr-table .lab-link {
  font-family: Consolas, Monaco, monospace;
  font-weight: 600;
  color: #0d6efd;
  text-decoration: none;
  font-size: 0.82rem;
}
.tr-table .lab-link:hover { text-decoration: underline; }
.tr-table .patient-name { font-weight: 700; }
.tr-table .patient-code {
  font-family: Consolas, Monaco, monospace;
  font-size: 0.72rem;
  color: #6c757d;
}
.tr-table .num {
  text-align: right;
  font-family: Consolas, Monaco, monospace;
  font-variant-numeric: tabular-nums;
}
.tr-table .center { text-align: center; }
.tr-table .muted { color: #6c757d; font-size: 0.75rem; }

/* Badges */
.tr-badge {
  display: inline-block;
  padding: 2px 8px;
  font-size: 0.66rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  border-radius: 0;
  text-transform: uppercase;
  color: #fff;
}
.tr-badge-approved { background: #198754; }
.tr-badge-completed { background: #0dcaf0; color: #055160; }
.tr-badge-correction { background: #ffc107; color: #664d03; }
.tr-badge-pending { background: #6c757d; }
.tr-badge-cancelled { background: #212529; }

/* Row actions */
.tr-actions {
  display: inline-flex;
  gap: 4px;
}
.tr-icon-btn {
  display: inline-block;
  padding: 4px 9px;
  font-size: 0.78rem;
  border: 1px solid #6c757d;
  background: #fff;
  color: #212529;
  text-decoration: none;
  border-radius: 0;
  cursor: pointer;
  line-height: 1;
}
.tr-icon-btn:hover { background: #f1f3f5; color: #212529; }
.tr-icon-btn-download {
  background: #dc3545;
  color: #fff;
  border-color: #dc3545;
}
.tr-icon-btn-download:hover { background: #b02a37; color: #fff; }

/* Empty */
.tr-empty {
  text-align: center;
  padding: 40px 20px;
  color: #6c757d;
  font-style: italic;
  border: 1.5px solid #212529;
  background: #fafbfc;
}

/* Media */
@media (max-width: 900px) {
  .tr-filter { grid-template-columns: 1fr; }
  .tr-table { font-size: 0.74rem; }
  .tr-table thead th,
  .tr-table tbody td { padding: 5px 7px; }
}
</style>
{% endblock %}

{% block content %}
<div class="tr-page">

  <div class="tr-header">
    <div>
      <h1 class="tr-title">
        <i class="bi bi-file-earmark-medical"></i> Test Reports
      </h1>
      <div class="tr-subtitle">Printable lab reports for approved orders</div>
    </div>
    <div class="tr-count">{{ orders|length }} report{{ 's' if orders|length != 1 }}</div>
  </div>

  {# Filters #}
  <form method="GET" class="tr-filter">
    <div class="tr-field">
      <label>Search</label>
      <input type="text" name="q" value="{{ q }}"
             placeholder="Lab # or patient name...">
    </div>
    <div class="tr-field">
      <label>Status</label>
      <select name="status">
        <option value="approved" {% if status == 'approved' %}selected{% endif %}>Approved (final)</option>
        <option value="completed" {% if status == 'completed' %}selected{% endif %}>Completed</option>
        <option value="correction" {% if status == 'correction' %}selected{% endif %}>Correction</option>
        <option value="all" {% if status == 'all' %}selected{% endif %}>All (non-cancelled)</option>
      </select>
    </div>
    <div class="tr-field">
      <button type="submit" class="tr-btn tr-btn-primary">
        <i class="bi bi-funnel"></i> Filter
      </button>
    </div>
  </form>

  {# Table #}
  {% if orders %}
  <table class="tr-table">
    <thead>
      <tr>
        <th style="width: 100px;">Lab #</th>
        <th>Patient</th>
        <th class="center" style="width: 70px;">Tests</th>
        <th class="end" style="width: 100px;">Total</th>
        <th class="center" style="width: 110px;">Status</th>
        <th style="width: 170px;">Reported</th>
        <th class="end" style="width: 150px;">Actions</th>
      </tr>
    </thead>
    <tbody>
      {% for o in orders %}
      <tr>
        <td>
          <a href="{{ url_for('orders.view_order', order_id=o.id) }}" class="lab-link">
            {{ o.order_code }}
          </a>
        </td>
        <td>
          <div class="patient-name">{{ o.patient.full_name }}</div>
          <div class="patient-code">{{ o.patient.patient_code }}</div>
        </td>
        <td class="center">
          <span class="muted">{{ o.item_count }}</span>
        </td>
        <td class="num">{{ o.final_total | money }}</td>
        <td class="center">
          {% set st = o.status|lower %}
          {% if st == 'approved' %}
            <span class="tr-badge tr-badge-approved">Approved</span>
          {% elif st == 'completed' %}
            <span class="tr-badge tr-badge-completed">Completed</span>
          {% elif st == 'correction' %}
            <span class="tr-badge tr-badge-correction">Correction</span>
          {% elif st == 'cancelled' %}
            <span class="tr-badge tr-badge-cancelled">Cancelled</span>
          {% else %}
            <span class="tr-badge tr-badge-pending">{{ o.status|capitalize }}</span>
          {% endif %}
        </td>
        <td class="muted" style="font-family: Consolas, Monaco, monospace; font-size: 0.76rem;">
          {% if o.reported_at %}{{ o.reported_at | localtime('%d-%b-%Y %I:%M %p') }}{% else %}—{% endif %}
        </td>
        <td class="end">
          <div class="tr-actions">
            <a href="{{ url_for('reports.view_pdf', order_id=o.id) }}"
               target="_blank"
               class="tr-icon-btn"
               title="Preview PDF">
              <i class="bi bi-eye"></i>
            </a>
            <a href="{{ url_for('reports.order_pdf', order_id=o.id) }}"
               class="tr-icon-btn tr-icon-btn-download"
               title="Download PDF">
              <i class="bi bi-download"></i>
            </a>
          </div>
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  {% else %}
  <div class="tr-empty">
    <i class="bi bi-inbox fs-3 d-block mb-2"></i>
    {% if q %}No reports match "{{ q }}".{% else %}No reports yet.{% endif %}
  </div>
  {% endif %}

</div>
{% endblock %}
"""

open(p, 'w', encoding='utf-8').write(new)
print('OK  - Test Reports page rewritten (dense classical)')

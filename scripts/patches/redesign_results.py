# Pending Results — dense classical redesign
p = 'modules/results/templates/results/index.html'
t = """{% extends 'base.html' %}
{% block title %}Pending Results — LabMS{% endblock %}

{% block head %}
<style>
/* ============================================================
   Pending Results — dense classical ledger layout
   ============================================================ */
.pr-page {
  max-width: 1500px;
  margin: 0 auto;
  padding: 10px 20px 30px;
  font-family: 'Segoe UI', Arial, sans-serif;
  font-size: 0.82rem;
  color: #212529;
}

/* Header */
.pr-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  border-bottom: 2px solid #212529;
  padding-bottom: 5px;
  margin-bottom: 10px;
  flex-wrap: wrap;
  gap: 8px;
}
.pr-title {
  font-size: 1.15rem;
  font-weight: 700;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}
.pr-subtitle { font-size: 0.76rem; color: #6c757d; margin-top: 2px; }
.pr-count {
  font-size: 0.76rem;
  color: #6c757d;
  font-family: Consolas, Monaco, monospace;
}

/* Filter strip */
.pr-filter {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  padding: 8px 10px;
  margin-bottom: 8px;
}
.pr-filter-row {
  display: grid;
  grid-template-columns: 2fr 1.2fr auto;
  gap: 8px;
  align-items: end;
}
.pr-field label {
  display: block;
  font-size: 0.62rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #6c757d;
  margin-bottom: 2px;
}
.pr-field input,
.pr-field select {
  width: 100%;
  padding: 3px 8px;
  border: 1px solid #6c757d;
  border-radius: 0;
  font-size: 0.82rem;
  background: #fff;
  height: 28px;
}
.pr-field input:focus,
.pr-field select:focus {
  outline: none;
  border-color: #198754;
}

/* Buttons */
.pr-btn {
  display: inline-block;
  padding: 4px 12px;
  font-size: 0.74rem;
  font-weight: 600;
  border: 1px solid #212529;
  background: #fff;
  color: #212529;
  text-decoration: none;
  border-radius: 0;
  cursor: pointer;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  height: 28px;
}
.pr-btn:hover { background: #f1f3f5; color: #212529; }
.pr-btn-primary { background: #198754; border-color: #198754; color: #fff; }
.pr-btn-primary:hover { background: #146c43; color: #fff; }
.pr-btn-danger { background: #fff; border-color: #dc3545; color: #dc3545; }
.pr-btn-danger:hover { background: #dc3545; color: #fff; }

/* Table */
.pr-table {
  width: 100%;
  border-collapse: collapse;
  border: 1.5px solid #212529;
  font-size: 0.78rem;
  background: #fff;
}
.pr-table thead th {
  background: #212529;
  color: #fff;
  font-size: 0.62rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 4px 8px;
  text-align: left;
  border: 1px solid #212529;
  white-space: nowrap;
}
.pr-table thead th.center { text-align: center; }
.pr-table thead th.end { text-align: right; }
.pr-table tbody td {
  padding: 3px 8px;
  border: 1px solid #adb5bd;
  vertical-align: middle;
}
.pr-table tbody tr.order-row:nth-child(even) { background: #fbfcfd; }
.pr-table tbody tr.order-row:hover { background: #f1f3f5; }
.pr-table code {
  font-size: 0.72rem;
  padding: 0 3px;
  font-family: Consolas, Monaco, monospace;
}
.pr-table .lab-link {
  color: #0d6efd;
  font-family: Consolas, Monaco, monospace;
  font-weight: 600;
  text-decoration: none;
  font-size: 0.78rem;
}
.pr-table .lab-link:hover { text-decoration: underline; }
.pr-table .name { font-weight: 700; font-size: 0.82rem; }
.pr-table .sub { font-size: 0.7rem; color: #6c757d; font-family: Consolas, Monaco, monospace; }
.pr-table .num {
  text-align: right;
  font-family: Consolas, Monaco, monospace;
  font-variant-numeric: tabular-nums;
}
.pr-table .center { text-align: center; }

/* Toggle column */
.pr-toggle-col { width: 30px; padding: 2px !important; text-align: center; }
.pr-toggle-btn {
  background: #fff;
  border: 1px solid #6c757d;
  color: #212529;
  width: 20px;
  height: 20px;
  padding: 0;
  border-radius: 0;
  line-height: 1;
  font-size: 0.68rem;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.pr-toggle-btn:hover { background: #e9ecef; }
.pr-toggle-btn.expanded { background: #212529; color: #fff; border-color: #212529; }

/* Badges */
.pr-badge {
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
.pr-badge-pending { background: #6c757d; }
.pr-badge-correction { background: #ffc107; color: #664d03; }

/* Row actions */
.pr-row-actions { display: inline-flex; gap: 3px; }
.pr-icon-btn {
  display: inline-block;
  padding: 2px 6px;
  font-size: 0.72rem;
  border: 1px solid #6c757d;
  background: #fff;
  color: #212529;
  text-decoration: none;
  border-radius: 0;
  cursor: pointer;
  line-height: 1;
}
.pr-icon-btn:hover { background: #f1f3f5; color: #212529; }
.pr-enter-btn {
  background: #198754;
  border-color: #198754;
  color: #fff;
  padding: 2px 10px;
  font-size: 0.72rem;
  font-weight: 600;
  border-radius: 0;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 3px;
}
.pr-enter-btn:hover { background: #146c43; color: #fff; }

/* Expanded row */
.pr-items-row td {
  padding: 0 !important;
  background: #f8f9fa;
  border: 1px solid #adb5bd;
}
.pr-items-inner {
  padding: 6px 12px 8px 44px;
}
.pr-test-line {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 3px 0;
  font-size: 0.78rem;
  border-bottom: 1px dashed #dee2e6;
}
.pr-test-line:last-child { border-bottom: none; }
.pr-test-line .test-icon {
  width: 14px;
  color: #6c757d;
  flex-shrink: 0;
}
.pr-test-line .test-name {
  font-weight: 500;
  flex: 1;
}
.pr-test-line .test-range,
.pr-test-line .test-unit {
  color: #6c757d;
  font-size: 0.72rem;
  min-width: 90px;
  font-family: Consolas, Monaco, monospace;
}
.pr-test-line .test-status {
  min-width: 90px;
  text-align: right;
  font-size: 0.72rem;
  color: #b02a37;
  font-weight: 600;
}
.pr-test-line.child { padding-left: 26px; }
.pr-test-line.child .test-name { font-weight: 400; }
.pr-test-line.panel-header .test-name {
  font-weight: 700;
  color: #0d6efd;
}
.pr-panel-badge {
  font-size: 0.6rem;
  padding: 1px 5px;
  border-radius: 0;
  background: #cff4fc;
  color: #055160;
  font-weight: 700;
  margin-left: 5px;
  text-transform: uppercase;
}

/* Empty state */
.pr-empty {
  text-align: center;
  padding: 30px 16px;
  color: #6c757d;
  font-style: italic;
  border: 1.5px solid #212529;
  background: #fafbfc;
}

@media (max-width: 900px) {
  .pr-filter-row { grid-template-columns: 1fr; }
  .pr-table { font-size: 0.72rem; }
  .pr-table thead th,
  .pr-table tbody td { padding: 3px 5px; }
  .pr-items-inner { padding-left: 30px; }
  .pr-test-line .test-range,
  .pr-test-line .test-unit { display: none; }
}
</style>
{% endblock %}

{% block content %}
<div class="pr-page">

  {# ============ HEADER ============ #}
  <div class="pr-header">
    <div>
      <h1 class="pr-title"><i class="bi bi-hourglass-split"></i> Pending Results</h1>
      <div class="pr-subtitle">Tests awaiting results entry</div>
    </div>
    <div class="pr-count">{{ pending_orders|length }} order{{ 's' if pending_orders|length != 1 }} pending</div>
  </div>

  {# ============ FILTERS ============ #}
  <form method="GET" action="{{ url_for('results.index') }}" class="pr-filter">
    <div class="pr-filter-row">
      <div class="pr-field">
        <label>Search</label>
        <input type="text" name="q" value="{{ q or '' }}"
               placeholder="Lab # / patient name / test name">
      </div>
      <div class="pr-field">
        <label>Status</label>
        <select name="order">
          <option value="">All pending</option>
          <option value="incomplete" {% if order_filter == 'incomplete' %}selected{% endif %}>Partially entered</option>
          <option value="empty"      {% if order_filter == 'empty' %}selected{% endif %}>Not started</option>
        </select>
      </div>
      <div class="pr-field">
        <button type="submit" class="pr-btn pr-btn-primary">
          <i class="bi bi-search"></i> Filter
        </button>
        {% if q or order_filter %}
        <a href="{{ url_for('results.index') }}" class="pr-btn pr-btn-danger ms-1">
          <i class="bi bi-x-lg"></i>
        </a>
        {% endif %}
      </div>
    </div>
  </form>

  {# ============ TABLE ============ #}
  {% if pending_orders %}
  <table class="pr-table">
    <thead>
      <tr>
        <th class="pr-toggle-col"></th>
        <th style="width: 100px;">Lab #</th>
        <th style="width: 100px;">Patient #</th>
        <th>Patient</th>
        <th class="center" style="width: 100px;">Pending</th>
        <th style="width: 130px;">Registered</th>
        <th class="end" style="width: 140px;">Actions</th>
      </tr>
    </thead>
    <tbody>
      {% for order in pending_orders %}
      <tr class="order-row">
        <td class="pr-toggle-col">
          <button type="button" class="pr-toggle-btn"
                  data-order-id="{{ order.id }}"
                  onclick="toggleOrder({{ order.id }})">
            <i class="bi bi-plus-lg"></i>
          </button>
        </td>
        <td>
          <a href="{{ url_for('orders.view_order', order_id=order.id) }}" class="lab-link">
            {{ order.order_code }}
          </a>
        </td>
        <td class="sub">{{ order.patient.patient_code }}</td>
        <td class="name">{{ order.patient.full_name }}</td>
        <td class="center">
          <span class="pr-badge pr-badge-pending">{{ order.pending_items|length }} test{{ 's' if order.pending_items|length != 1 }}</span>
          {% if order.status == 'correction' %}
            <span class="pr-badge pr-badge-correction">Correction</span>
          {% endif %}
        </td>
        <td class="sub" style="font-size: 0.72rem;">
          {{ order.created_at | localtime('%d/%m/%y %H:%M') }}
        </td>
        <td class="end">
          <div class="pr-row-actions">
            <a href="{{ url_for('orders.view_order', order_id=order.id) }}"
               class="pr-icon-btn" title="View Order">
              <i class="bi bi-eye"></i>
            </a>
            <a href="{{ url_for('results.enter', order_id=order.id) }}" class="pr-enter-btn">
              <i class="bi bi-pencil-square"></i> Enter
            </a>
          </div>
        </td>
      </tr>

      {# ---- Inline items preview (hidden by default) ---- #}
      <tr class="pr-items-row" id="items-row-{{ order.id }}" style="display:none;">
        <td colspan="7">
          <div class="pr-items-inner">
            {% for item in order.pending_items %}
              {% if item.has_children %}
                <div class="pr-test-line panel-header">
                  <span class="test-icon"><i class="bi bi-collection"></i></span>
                  <span class="test-name">
                    {{ item.test.name }}
                    <span class="pr-panel-badge">{{ item.children|length }} params</span>
                  </span>
                  <span class="test-range"></span>
                  <span class="test-unit"></span>
                  <span class="test-status"></span>
                </div>
                {% for child in item.children %}
                  {% if not child.result_value %}
                  <div class="pr-test-line child">
                    <span class="test-icon"><i class="bi bi-arrow-return-right"></i></span>
                    <span class="test-name">{{ child.test.name }}</span>
                    <span class="test-range">{{ child.test.normal_range or '—' }}</span>
                    <span class="test-unit">{{ child.test.unit or '—' }}</span>
                    <span class="test-status">Pending</span>
                  </div>
                  {% endif %}
                {% endfor %}
              {% else %}
                <div class="pr-test-line">
                  <span class="test-icon"><i class="bi bi-droplet"></i></span>
                  <span class="test-name">{{ item.test.name }}</span>
                  <span class="test-range">{{ item.test.normal_range or '—' }}</span>
                  <span class="test-unit">{{ item.test.unit or '—' }}</span>
                  <span class="test-status">Pending</span>
                </div>
              {% endif %}
            {% endfor %}
          </div>
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  {% else %}
  <div class="pr-empty">
    <i class="bi bi-check2-circle fs-3 d-block mb-2 text-success"></i>
    <div class="fw-semibold">No pending results</div>
    <div class="small">All caught up. 🎉</div>
  </div>
  {% endif %}

</div>
{% endblock %}

{% block scripts %}
<script>
(function () {
  'use strict';
  var STORAGE_KEY = 'labms_pending_results_expanded';

  function loadExpanded() {
    try {
      var raw = sessionStorage.getItem(STORAGE_KEY);
      return raw ? (JSON.parse(raw) || {}) : {};
    } catch (_) { return {}; }
  }
  function saveExpanded(set) {
    try { sessionStorage.setItem(STORAGE_KEY, JSON.stringify(set)); } catch (_) {}
  }
  function applyState(orderId, expanded) {
    var row = document.getElementById('items-row-' + orderId);
    var btn = document.querySelector('button.pr-toggle-btn[data-order-id="' + orderId + '"]');
    if (!row || !btn) return;
    if (expanded) {
      row.style.display = 'table-row';
      btn.classList.add('expanded');
      btn.innerHTML = '<i class="bi bi-dash-lg"></i>';
    } else {
      row.style.display = 'none';
      btn.classList.remove('expanded');
      btn.innerHTML = '<i class="bi bi-plus-lg"></i>';
    }
  }
  window.toggleOrder = function (orderId) {
    var set = loadExpanded();
    var open = !!set[orderId];
    if (open) delete set[orderId];
    else set[orderId] = 1;
    saveExpanded(set);
    applyState(orderId, !open);
  };
  document.addEventListener('DOMContentLoaded', function () {
    var set = loadExpanded();
    Object.keys(set).forEach(function (orderId) { applyState(orderId, true); });
  });
})();
</script>
{% endblock %}
"""

open(p, 'w', encoding='utf-8').write(t)
print('OK  - results index.html rewritten (dense classical)')

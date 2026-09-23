# Pending Verification — dense classical redesign
p = 'modules/lab/templates/lab/verify.html'
t = """{% extends 'base.html' %}
{% block title %}Pending Verification — LabMS{% endblock %}

{% block head %}
<style>
/* ============================================================
   Pending Verification — dense classical ledger layout
   ============================================================ */
.lv-page {
  max-width: 1500px;
  margin: 0 auto;
  padding: 10px 20px 30px;
  font-family: 'Segoe UI', Arial, sans-serif;
  font-size: 0.82rem;
  color: #212529;
}

/* Header */
.lv-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  border-bottom: 2px solid #212529;
  padding-bottom: 5px;
  margin-bottom: 10px;
  flex-wrap: wrap;
  gap: 8px;
}
.lv-title {
  font-size: 1.15rem;
  font-weight: 700;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}
.lv-subtitle { font-size: 0.76rem; color: #6c757d; margin-top: 2px; }
.lv-count {
  font-size: 0.76rem;
  color: #6c757d;
  font-family: Consolas, Monaco, monospace;
}

/* Filter strip */
.lv-filter {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  padding: 8px 10px;
  margin-bottom: 8px;
}
.lv-filter-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr auto;
  gap: 8px;
  align-items: end;
}
.lv-field label {
  display: block;
  font-size: 0.62rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #6c757d;
  margin-bottom: 2px;
}
.lv-field input,
.lv-field select {
  width: 100%;
  padding: 3px 8px;
  border: 1px solid #6c757d;
  border-radius: 0;
  font-size: 0.82rem;
  background: #fff;
  height: 28px;
}
.lv-field input:focus,
.lv-field select:focus {
  outline: none;
  border-color: #198754;
}

/* Buttons */
.lv-btn {
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
.lv-btn:hover { background: #f1f3f5; color: #212529; }
.lv-btn-primary { background: #198754; border-color: #198754; color: #fff; }
.lv-btn-primary:hover { background: #146c43; color: #fff; }
.lv-btn-bulk { background: #198754; border-color: #198754; color: #fff; }
.lv-btn-bulk:hover { background: #146c43; color: #fff; }
.lv-btn-sendback { background: #fff; border-color: #ffc107; color: #664d03; }
.lv-btn-sendback:hover { background: #ffc107; color: #664d03; }
.lv-btn-danger { background: #fff; border-color: #dc3545; color: #dc3545; }
.lv-btn-danger:hover { background: #dc3545; color: #fff; }

/* Bulk action bar */
.lv-bulkbar {
  background: #e7f1ff;
  border: 1px solid #0d6efd;
  padding: 6px 12px;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.78rem;
}
.lv-bulkbar .count {
  font-family: Consolas, Monaco, monospace;
  font-weight: 700;
  color: #0d6efd;
}
.lv-bulkbar .btn-row { display: flex; gap: 6px; margin-left: auto; }

/* Table */
.lv-table {
  width: 100%;
  border-collapse: collapse;
  border: 1.5px solid #212529;
  font-size: 0.78rem;
  background: #fff;
}
.lv-table thead th {
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
.lv-table thead th.center { text-align: center; }
.lv-table thead th.end { text-align: right; }
.lv-table tbody td {
  padding: 3px 8px;
  border: 1px solid #adb5bd;
  vertical-align: middle;
}
.lv-table tbody tr.order-row:nth-child(even) { background: #fbfcfd; }
.lv-table tbody tr.order-row:hover { background: #f1f3f5; }
.lv-table tbody tr.order-row.has-correction { background: #fff8e1; }
.lv-table code {
  font-size: 0.72rem;
  padding: 0 3px;
  font-family: Consolas, Monaco, monospace;
}
.lv-table .lab-link {
  color: #0d6efd;
  font-family: Consolas, Monaco, monospace;
  font-weight: 600;
  text-decoration: none;
  font-size: 0.78rem;
}
.lv-table .lab-link:hover { text-decoration: underline; }
.lv-table .name { font-weight: 700; font-size: 0.82rem; }
.lv-table .sub { font-size: 0.7rem; color: #6c757d; font-family: Consolas, Monaco, monospace; }
.lv-table .center { text-align: center; }

/* Toggle column */
.lv-toggle-col { width: 30px; padding: 2px !important; text-align: center; }
.lv-toggle-btn {
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
.lv-toggle-btn:hover { background: #e9ecef; }
.lv-toggle-btn.expanded { background: #212529; color: #fff; border-color: #212529; }

/* Badges */
.lv-badge {
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
.lv-badge-correction { background: #ffc107; color: #664d03; }
.lv-badge-pending { background: #6c757d; }

/* Expanded row */
.lv-items-row td {
  padding: 0 !important;
  background: #f8f9fa;
  border: 1px solid #adb5bd;
}
.lv-items-inner {
  padding: 6px 12px 8px 44px;
}
.lv-test-line {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 3px 0;
  font-size: 0.78rem;
  border-bottom: 1px dashed #dee2e6;
}
.lv-test-line:last-child { border-bottom: none; }
.lv-test-line .test-icon { width: 14px; color: #6c757d; flex-shrink: 0; }
.lv-test-line .test-name { font-weight: 500; flex: 1; }
.lv-test-line .test-range,
.lv-test-line .test-unit {
  color: #6c757d;
  font-size: 0.72rem;
  min-width: 90px;
  font-family: Consolas, Monaco, monospace;
}
.lv-test-line .test-result {
  color: #146c43;
  font-weight: 700;
  min-width: 80px;
  text-align: right;
  font-family: Consolas, Monaco, monospace;
}
.lv-test-line .test-action {
  min-width: 130px;
  text-align: right;
}
.lv-test-line.child { padding-left: 26px; }
.lv-test-line.child .test-name { font-weight: 400; }
.lv-test-line.panel-header .test-name { font-weight: 700; color: #0d6efd; }
.lv-panel-badge {
  font-size: 0.6rem;
  padding: 1px 5px;
  border-radius: 0;
  background: #cff4fc;
  color: #055160;
  font-weight: 700;
  margin-left: 5px;
  text-transform: uppercase;
}

/* Small inline buttons in expand */
.lv-mini-btn {
  padding: 1px 7px;
  font-size: 0.68rem;
  border-radius: 0;
  border: 1px solid #198754;
  background: #198754;
  color: #fff;
  text-decoration: none;
  cursor: pointer;
  font-weight: 600;
}
.lv-mini-btn:hover { background: #146c43; border-color: #146c43; color: #fff; }
.lv-mini-btn-warn { background: #fff; border-color: #ffc107; color: #664d03; }
.lv-mini-btn-warn:hover { background: #ffc107; color: #664d03; }
.lv-mini-checkbox { transform: scale(0.9); }

/* Empty state */
.lv-empty {
  text-align: center;
  padding: 30px 16px;
  color: #6c757d;
  font-style: italic;
  border: 1.5px solid #212529;
  background: #fafbfc;
}

@media (max-width: 900px) {
  .lv-filter-row { grid-template-columns: 1fr; }
  .lv-table { font-size: 0.72rem; }
  .lv-table thead th,
  .lv-table tbody td { padding: 3px 5px; }
  .lv-items-inner { padding-left: 30px; }
  .lv-test-line .test-range,
  .lv-test-line .test-unit { display: none; }
}
</style>
{% endblock %}

{% block content %}
<div class="lv-page">

  {# ============ HEADER ============ #}
  <div class="lv-header">
    <div>
      <h1 class="lv-title"><i class="bi bi-clipboard2-check"></i> Pending Verification</h1>
      <div class="lv-subtitle">Tests with results — awaiting pathologist approval</div>
    </div>
    <div class="lv-count">{{ items|length }} item{{ 's' if items|length != 1 }} in {{ orders|length }} order{{ 's' if orders|length != 1 }}</div>
  </div>

  {# ============ FILTERS ============ #}
  <form method="GET" action="{{ url_for('lab.verify_queue') }}" class="lv-filter" id="verifyForm">
    <div class="lv-filter-row">
      <div class="lv-field">
        <label>Search</label>
        <input type="text" name="q" value="{{ q or '' }}"
               placeholder="Lab # / patient name / patient #">
      </div>
      <div class="lv-field">
        <label>From</label>
        <input type="date" name="date_from" value="{{ date_from or '' }}">
      </div>
      <div class="lv-field">
        <label>To</label>
        <input type="date" name="date_to" value="{{ date_to or today }}">
      </div>
      <div class="lv-field">
        <button type="submit" class="lv-btn lv-btn-primary">
          <i class="bi bi-search"></i> Filter
        </button>
      </div>
    </div>
  </form>

  {# ============ BULK ACTION BAR ============ #}
  {% if items %}
  <div class="lv-bulkbar" id="bulkBar">
    <span class="count" id="bulkCount">0</span> item(s) selected
    <div class="btn-row">
      <button type="button" class="lv-btn lv-btn-bulk" onclick="bulkApprove()">
        <i class="bi bi-check-lg"></i> Approve Selected
      </button>
      <button type="button" class="lv-btn lv-btn-sendback" onclick="openBulkSendBack()">
        <i class="bi bi-arrow-return-left"></i> Send Back
      </button>
    </div>
  </div>
  {% endif %}

  {# ============ TABLE ============ #}
  {% if orders %}
  <table class="lv-table">
    <thead>
      <tr>
        <th class="lv-toggle-col"></th>
        <th class="center" style="width: 40px;">
          <input type="checkbox" id="checkAll" class="lv-mini-checkbox"
                 onchange="toggleAll(this.checked);">
        </th>
        <th style="width: 100px;">Lab #</th>
        <th>Patient</th>
        <th style="width: 100px;">Patient #</th>
        <th class="center" style="width: 100px;">Pending</th>
        <th style="width: 130px;">Registered</th>
      </tr>
    </thead>
    <tbody>
      {% for order in orders %}
      {% set has_corr = order.pending_items|selectattr('needs_correction')|list|length > 0 %}
      <tr class="order-row {% if has_corr %}has-correction{% endif %}">
        <td class="lv-toggle-col">
          <button type="button" class="lv-toggle-btn"
                  data-order-id="{{ order.id }}"
                  onclick="toggleOrder({{ order.id }})">
            <i class="bi bi-plus-lg"></i>
          </button>
        </td>
        <td class="center">
          <input type="checkbox" class="lv-mini-checkbox item-check"
                 value="{{ order.id }}"
                 onchange="updateBulkCount();">
        </td>
        <td>
          <a href="{{ url_for('orders.view_order', order_id=order.id) }}" class="lab-link">
            {{ order.order_code }}
          </a>
        </td>
        <td class="name">{{ order.patient.full_name }}</td>
        <td class="sub">{{ order.patient.patient_code }}</td>
        <td class="center">
          <span class="lv-badge lv-badge-pending">{{ order.pending_items|length }} item{{ 's' if order.pending_items|length != 1 }}</span>
          {% if has_corr %}
            <span class="lv-badge lv-badge-correction">Correction</span>
          {% endif %}
        </td>
        <td class="sub" style="font-size: 0.72rem;">
          {{ order.created_at | localtime('%d/%m/%y %H:%M') }}
        </td>
      </tr>

      <tr class="lv-items-row" id="items-row-{{ order.id }}" style="display:none;">
        <td colspan="7">
          <div class="lv-items-inner">
            {% for item in order.pending_items %}
              {% if item.has_children %}
                <div class="lv-test-line panel-header">
                  <span class="test-icon"><i class="bi bi-collection"></i></span>
                  <span class="test-name">
                    {{ item.test.name }}
                    <span class="lv-panel-badge">{{ item.children|length }} params</span>
                  </span>
                  <span class="test-range"></span>
                  <span class="test-unit"></span>
                  <span class="test-result"></span>
                  <span class="test-action">
                    <button type="button" class="lv-mini-btn"
                            onclick="approveItem({{ item.id }})">
                      <i class="bi bi-check-lg"></i> Approve
                    </button>
                    <button type="button" class="lv-mini-btn lv-mini-btn-warn"
                            onclick="sendBackItem({{ item.id }})">
                      <i class="bi bi-arrow-return-left"></i> Send Back
                    </button>
                  </span>
                </div>
                {% for child in item.children %}
                <div class="lv-test-line child">
                  <span class="test-icon"><i class="bi bi-arrow-return-right"></i></span>
                  <span class="test-name">{{ child.test.name }}</span>
                  <span class="test-range">{{ child.test.normal_range or '—' }}</span>
                  <span class="test-unit">{{ child.test.unit or '—' }}</span>
                  <span class="test-result">{{ child.result_value or '—' }}</span>
                  <span class="test-action"></span>
                </div>
                {% endfor %}
              {% else %}
                <div class="lv-test-line">
                  <span class="test-icon"><i class="bi bi-droplet"></i></span>
                  <span class="test-name">{{ item.test.name }}</span>
                  <span class="test-range">{{ item.test.normal_range or '—' }}</span>
                  <span class="test-unit">{{ item.test.unit or '—' }}</span>
                  <span class="test-result">{{ item.result_value or '—' }}</span>
                  <span class="test-action">
                    <button type="button" class="lv-mini-btn"
                            onclick="approveItem({{ item.id }})">
                      <i class="bi bi-check-lg"></i> Approve
                    </button>
                    <button type="button" class="lv-mini-btn lv-mini-btn-warn"
                            onclick="sendBackItem({{ item.id }})">
                      <i class="bi bi-arrow-return-left"></i> Send Back
                    </button>
                  </span>
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
  <div class="lv-empty">
    <i class="bi bi-check2-circle fs-3 d-block mb-2 text-success"></i>
    <div class="fw-semibold">All caught up</div>
    <div class="small">No tests awaiting verification in this range.</div>
  </div>
  {% endif %}

</div>

{# ============ SEND BACK MODAL ============ #}
<div class="modal fade" id="sendBackModal" tabindex="-1">
  <div class="modal-dialog">
    <form method="POST" id="sendBackForm">
      <div class="modal-content" style="border-radius:0;">
        <div class="modal-header">
          <h5 class="modal-title"><i class="bi bi-arrow-return-left text-warning"></i> Send Back for Correction</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <label class="form-label fw-semibold">Reason <span class="text-danger">*</span></label>
          <textarea name="reason" class="form-control" rows="3" required
                    placeholder="e.g. Value looks wrong, please repeat the test..."></textarea>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Cancel</button>
          <button type="submit" class="btn btn-warning">Send Back</button>
        </div>
      </div>
    </form>
  </div>
</div>
{% endblock %}

{% block scripts %}
<script>
(function () {
  'use strict';
  var STORAGE_KEY = 'labms_verify_expanded';

  function loadExpanded() {
    try { var r = sessionStorage.getItem(STORAGE_KEY); return r ? JSON.parse(r) : {}; }
    catch (_) { return {}; }
  }
  function saveExpanded(s) {
    try { sessionStorage.setItem(STORAGE_KEY, JSON.stringify(s)); } catch (_) {}
  }
  function applyState(orderId, expanded) {
    var row = document.getElementById('items-row-' + orderId);
    var btn = document.querySelector('button.lv-toggle-btn[data-order-id="' + orderId + '"]');
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
    Object.keys(set).forEach(function (id) { applyState(id, true); });
  });

  window.updateBulkCount = function () {
    var n = document.querySelectorAll('.item-check:checked').length;
    var el = document.getElementById('bulkCount');
    if (el) el.textContent = n;
  };
  window.toggleAll = function (checked) {
    document.querySelectorAll('.item-check').forEach(function (c) { c.checked = checked; });
    updateBulkCount();
  };

  window.bulkApprove = function () {
    var ids = Array.from(document.querySelectorAll('.item-check:checked')).map(function (c) { return c.value; });
    if (!ids.length) { alert('Select at least one order.'); return; }
    if (!confirm('Approve all pending items in the selected order(s)?')) return;

    var form = document.createElement('form');
    form.method = 'POST';
    form.action = '/lab/verify/bulk-approve';
    ids.forEach(function (id) {
      var inp = document.createElement('input');
      inp.type = 'hidden';
      inp.name = 'item_ids';
      inp.value = id;
      form.appendChild(inp);
    });
    document.body.appendChild(form);
    form.submit();
  };

  window.approveItem = function (itemId) {
    if (!confirm('Approve this item?')) return;
    var form = document.createElement('form');
    form.method = 'POST';
    form.action = '/lab/verify/bulk-approve';
    var inp = document.createElement('input');
    inp.type = 'hidden';
    inp.name = 'item_ids';
    inp.value = itemId;
    form.appendChild(inp);
    document.body.appendChild(form);
    form.submit();
  };

  window.sendBackItem = function (itemId) {
    var form = document.getElementById('sendBackForm');
    form.action = '/lab/verify/send-back/' + itemId;
    var modal = new bootstrap.Modal(document.getElementById('sendBackModal'));
    modal.show();
  };

  window.openBulkSendBack = function () {
    var ids = Array.from(document.querySelectorAll('.item-check:checked')).map(function (c) { return c.value; });
    if (!ids.length) { alert('Select at least one order.'); return; }
    // Redirect to send-back for the first selected (bulk send-back not implemented per row here)
    sendBackItem(ids[0]);
  };
})();
</script>
{% endblock %}
"""

open(p, 'w', encoding='utf-8').write(t)
print('OK  - verify.html rewritten (dense classical)')

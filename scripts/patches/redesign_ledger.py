# Daily Ledger — full dense classical redesign
p = 'modules/orders/templates/orders/list.html'
t = """{% extends 'base.html' %}
{% block title %}Daily Ledger — LabMS{% endblock %}

{% block head %}
<style>
/* ============================================================
   Daily Ledger — dense classical ledger layout
   ============================================================ */
.dl-page {
  max-width: 1500px;
  margin: 0 auto;
  padding: 10px 20px 30px;
  font-family: 'Segoe UI', Arial, sans-serif;
  font-size: 0.82rem;
  color: #212529;
}

/* Header */
.dl-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  border-bottom: 2px solid #212529;
  padding-bottom: 5px;
  margin-bottom: 10px;
  flex-wrap: wrap;
  gap: 8px;
}
.dl-title {
  font-size: 1.15rem;
  font-weight: 700;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}
.dl-subtitle { font-size: 0.76rem; color: #6c757d; margin-top: 2px; }
.dl-count {
  font-size: 0.76rem;
  color: #6c757d;
  font-family: Consolas, Monaco, monospace;
}

/* Filter strip */
.dl-filter {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  padding: 8px 10px;
  margin-bottom: 8px;
}
.dl-filter-row {
  display: grid;
  grid-template-columns: 130px 130px 2fr 1.2fr 1fr auto;
  gap: 8px;
  align-items: end;
}
.dl-field label {
  display: block;
  font-size: 0.62rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #6c757d;
  margin-bottom: 2px;
}
.dl-field input,
.dl-field select {
  width: 100%;
  padding: 3px 8px;
  border: 1px solid #6c757d;
  border-radius: 0;
  font-size: 0.82rem;
  background: #fff;
  height: 28px;
}
.dl-field input:focus,
.dl-field select:focus {
  outline: none;
  border-color: #198754;
}

/* Quick filters */
.dl-quick {
  display: flex;
  gap: 4px;
  margin-top: 6px;
  flex-wrap: wrap;
}
.dl-quick a {
  display: inline-block;
  padding: 2px 8px;
  font-size: 0.72rem;
  border: 1px solid #adb5bd;
  background: #fff;
  color: #212529;
  text-decoration: none;
  border-radius: 0;
  cursor: pointer;
}
.dl-quick a:hover { background: #f1f3f5; }
.dl-quick a.active { background: #212529; color: #fff; border-color: #212529; }

/* Buttons */
.dl-btn {
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
.dl-btn:hover { background: #f1f3f5; color: #212529; }
.dl-btn-primary { background: #198754; border-color: #198754; color: #fff; }
.dl-btn-primary:hover { background: #146c43; color: #fff; }
.dl-btn-clear { background: #fff; border-color: #dc3545; color: #dc3545; }
.dl-btn-clear:hover { background: #dc3545; color: #fff; }

/* Table */
.dl-table {
  width: 100%;
  border-collapse: collapse;
  border: 1.5px solid #212529;
  font-size: 0.78rem;
  background: #fff;
}
.dl-table thead th {
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
.dl-table thead th.num { text-align: right; }
.dl-table thead th.center { text-align: center; }
.dl-table tbody td {
  padding: 3px 8px;
  border: 1px solid #adb5bd;
  vertical-align: middle;
}
.dl-table tbody tr:nth-child(even) { background: #fbfcfd; }
.dl-table tbody tr:hover { background: #f1f3f5; }
.dl-table tbody tr.cancelled-row td { background: #f8f9fa !important; opacity: 0.75; }
.dl-table code {
  font-size: 0.72rem;
  padding: 0 3px;
  font-family: Consolas, Monaco, monospace;
}
.dl-table .name { font-weight: 700; font-size: 0.82rem; }
.dl-table .sub { font-size: 0.7rem; color: #6c757d; }
.dl-table .num {
  text-align: right;
  font-family: Consolas, Monaco, monospace;
  font-variant-numeric: tabular-nums;
}
.dl-table .center { text-align: center; }
.dl-table .strike { text-decoration: line-through; color: #adb5bd !important; }
.dl-table .due { color: #b02a37; font-weight: 700; }
.dl-table .paid-ok { color: #146c43; font-weight: 600; }

/* Badges */
.dl-badge {
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
.dl-badge-pending { background: #ffc107; color: #664d03; }
.dl-badge-collected { background: #0dcaf0; color: #055160; }
.dl-badge-completed { background: #0dcaf0; color: #055160; }
.dl-badge-approved { background: #198754; }
.dl-badge-correction { background: #ffc107; color: #664d03; }
.dl-badge-cancelled { background: #6c757d; }
.dl-badge-paid { background: #198754; }
.dl-badge-unpaid { background: #dc3545; }
.dl-badge-partial { background: #ffc107; color: #664d03; }

/* Row actions dropdown */
.dl-actions .btn {
  padding: 1px 6px;
  font-size: 0.72rem;
  border-radius: 0;
  line-height: 1;
}
.dl-actions .dropdown-menu {
  font-size: 0.8rem;
  border-radius: 0;
  padding: 2px 0;
  border: 1px solid #212529;
}
.dl-actions .dropdown-item {
  padding: 4px 12px;
  font-size: 0.78rem;
}
.dl-actions .dropdown-item i { width: 16px; }

/* Empty state */
.dl-empty {
  text-align: center;
  padding: 30px 16px;
  color: #6c757d;
  font-style: italic;
}

/* Footer summary */
.dl-summary {
  background: #f8f9fa;
  border: 1.5px solid #212529;
  border-top: none;
  padding: 6px 12px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 4px 18px;
  font-size: 0.78rem;
}
.dl-summary .stat { display: flex; justify-content: space-between; align-items: baseline; gap: 8px; }
.dl-summary .label {
  font-size: 0.64rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #6c757d;
}
.dl-summary .value {
  font-family: Consolas, Monaco, monospace;
  font-variant-numeric: tabular-nums;
  font-weight: 700;
  font-size: 0.86rem;
}
.dl-summary .value.success { color: #146c43; }
.dl-summary .value.danger { color: #b02a37; }

@media (max-width: 1100px) {
  .dl-filter-row { grid-template-columns: 1fr 1fr 1fr; }
  .dl-table { font-size: 0.72rem; }
  .dl-table thead th,
  .dl-table tbody td { padding: 3px 5px; }
}
</style>
{% endblock %}

{% block content %}
<div class="dl-page">

  {# ============ HEADER ============ #}
  <div class="dl-header">
    <div>
      <h1 class="dl-title"><i class="bi bi-journal-text"></i> Daily Ledger</h1>
      <div class="dl-subtitle">Registrations and payment status between selected dates</div>
    </div>
    <div class="dl-count">{{ orders|length }} registration{{ 's' if orders|length != 1 }} in this range</div>
  </div>

  {# ============ FILTER STRIP ============ #}
  <form method="GET" action="{{ url_for('orders.list_orders') }}" class="dl-filter">
    <div class="dl-filter-row">
      <div class="dl-field">
        <label>From</label>
        <input type="date" name="date_from" value="{{ date_from }}">
      </div>
      <div class="dl-field">
        <label>To</label>
        <input type="date" name="date_to" value="{{ date_to }}">
      </div>
      <div class="dl-field">
        <label>Search</label>
        <input type="text" name="q" value="{{ q }}" placeholder="Lab # / patient / mobile">
      </div>
      <div class="dl-field">
        <label>Status</label>
        <select name="status">
          <option value="">All</option>
          {% for s in statuses %}
          <option value="{{ s }}" {% if status == s %}selected{% endif %}>{{ s|capitalize }}</option>
          {% endfor %}
        </select>
      </div>
      <div class="dl-field">
        <label>Paid</label>
        <select name="paid">
          <option value="">Any</option>
          <option value="yes" {% if paid_filter == 'yes' %}selected{% endif %}>Paid</option>
          <option value="no"  {% if paid_filter == 'no'  %}selected{% endif %}>Unpaid</option>
          <option value="partial" {% if paid_filter == 'partial' %}selected{% endif %}>Partial</option>
        </select>
      </div>
      <div class="dl-field">
        <button type="submit" class="dl-btn dl-btn-primary">
          <i class="bi bi-search"></i> Filter
        </button>
      </div>
    </div>

    {# Quick date links #}
    <div class="dl-quick">
      <a href="{{ url_for('orders.list_orders', date_from=today, date_to=today) }}">Today</a>
      <a href="{{ url_for('orders.list_orders', date_from=yesterday, date_to=yesterday) if yesterday is defined else url_for('orders.list_orders') }}">Yesterday</a>
      <a href="{{ url_for('orders.list_orders', date_from=last7, date_to=today) if last7 is defined else url_for('orders.list_orders') }}">Last 7 days</a>
      <a href="{{ url_for('orders.list_orders', date_from=last30, date_to=today) if last30 is defined else url_for('orders.list_orders') }}">Last 30 days</a>
      <a href="{{ url_for('orders.list_orders', date_from=month_start, date_to=today) if month_start is defined else url_for('orders.list_orders') }}">This month</a>
      {% if q or status or paid_filter %}
      <a href="{{ url_for('orders.list_orders') }}" class="dl-btn-clear" style="margin-left:auto; padding: 2px 8px; font-size: 0.72rem;">
        <i class="bi bi-x-lg"></i> Clear filters
      </a>
      {% endif %}
    </div>
  </form>

  {# ============ TABLE ============ #}
  {% if orders %}
  <table class="dl-table">
    <thead>
      <tr>
        <th style="width: 90px;">Lab #</th>
        <th>Patient</th>
        <th style="width: 100px;">Patient #</th>
        <th style="width: 110px;">Mobile</th>
        <th class="center" style="width: 50px;">Items</th>
        <th class="num" style="width: 80px;">Total</th>
        <th class="num" style="width: 80px;">Discount</th>
        <th class="num" style="width: 80px;">Net</th>
        <th class="num" style="width: 80px;">Paid</th>
        <th class="num" style="width: 80px;">Due</th>
        <th style="width: 90px;">Status</th>
        <th style="width: 80px;">Payment</th>
        <th style="width: 110px;">Registered</th>
        <th class="center" style="width: 50px;"></th>
      </tr>
    </thead>
    <tbody>
      {% for o in orders %}
      <tr class="{% if o.status == 'cancelled' %}cancelled-row{% endif %}">
        <td><code>{{ o.order_code }}</code></td>
        <td class="name">{{ o.patient.full_name }}</td>
        <td class="sub" style="font-family: Consolas, Monaco, monospace;">{{ o.patient.patient_code }}</td>
        <td class="sub" style="font-family: Consolas, Monaco, monospace;">{{ o.patient.phone or '—' }}</td>
        <td class="center">
          <span class="dl-badge" style="background:#e9ecef; color:#495057;">{{ o.item_count }}</span>
        </td>
        <td class="num {% if o.status == 'cancelled' %}strike{% endif %}">{{ o.subtotal | money }}</td>
        <td class="num {% if o.status == 'cancelled' %}strike{% endif %}">{% if o.discount_value %}{{ o.discount_value | money }}{% else %}—{% endif %}</td>
        <td class="num {% if o.status == 'cancelled' %}strike{% endif %}">{{ o.final_total | money }}</td>
        <td class="num paid-ok">
          {% if o.status == 'cancelled' %}<span class="strike">refunded</span>
          {% elif o.paid_amount %}{{ o.paid_amount | money }}
          {% else %}—{% endif %}
        </td>
        <td class="num">
          {% if o.status == 'cancelled' %}<span class="strike">—</span>
          {% elif o.balance_due > 0.01 %}<span class="due">{{ o.balance_due | money }}</span>
          {% else %}—{% endif %}
        </td>
        <td>
          {% set st = o.status|lower %}
          {% if st == 'pending' %}<span class="dl-badge dl-badge-pending">Pending</span>
          {% elif st == 'collected' %}<span class="dl-badge dl-badge-collected">Collected</span>
          {% elif st == 'completed' %}<span class="dl-badge dl-badge-completed">Completed</span>
          {% elif st == 'approved' %}<span class="dl-badge dl-badge-approved">Approved</span>
          {% elif st == 'correction' %}<span class="dl-badge dl-badge-correction">Correction</span>
          {% elif st == 'cancelled' %}<span class="dl-badge dl-badge-cancelled">Cancelled</span>
          {% else %}<span class="dl-badge" style="background:#e9ecef; color:#495057;">{{ o.status }}</span>
          {% endif %}
        </td>
        <td>
          {% if o.status == 'cancelled' %}<span class="dl-badge dl-badge-cancelled">Cancelled</span>
          {% elif o.payment_status == 'paid' %}<span class="dl-badge dl-badge-paid">Paid</span>
          {% elif o.payment_status == 'partial' %}<span class="dl-badge dl-badge-partial">Partial</span>
          {% else %}<span class="dl-badge dl-badge-unpaid">Unpaid</span>
          {% endif %}
        </td>
        <td class="sub" style="font-family: Consolas, Monaco, monospace; font-size: 0.7rem;">
          {{ o.created_at | localtime('%d/%m/%y %H:%M') }}
        </td>
        <td class="center dl-actions">
          <div class="dropdown">
            <button class="btn btn-sm btn-outline-primary py-0 px-1 dropdown-toggle"
                    type="button" data-bs-toggle="dropdown" data-bs-strategy="fixed"
                    aria-expanded="false" title="Actions">
              <i class="bi bi-eye" style="font-size:0.72rem;"></i>
            </button>
            <ul class="dropdown-menu dropdown-menu-end">

              <li>
                <a class="dropdown-item" href="{{ url_for('orders.view_order', order_id=o.id) }}">
                  <i class="bi bi-file-earmark-text"></i> View Details
                </a>
              </li>

              {% if o.status != 'cancelled' and (not o.has_any_results or o.edit_unlocked) %}
              <li>
                <a class="dropdown-item" href="{{ url_for('orders.edit_order', order_id=o.id) }}">
                  <i class="bi bi-pencil-square text-primary"></i> Edit Order
                </a>
              </li>
              {% endif %}

              <li><hr class="dropdown-divider"></li>

              <li>
                <a class="dropdown-item" href="{{ url_for('orders.print_order', order_id=o.id, copy='patient', auto=1) }}" target="_blank" rel="noopener">
                  <i class="bi bi-person-vcard text-primary"></i> Patient Bill
                </a>
              </li>
              <li>
                <a class="dropdown-item" href="{{ url_for('orders.print_order', order_id=o.id, copy='lab', auto=1) }}" target="_blank" rel="noopener">
                  <i class="bi bi-clipboard2-pulse text-success"></i> Lab Bill
                </a>
              </li>
              <li>
                <a class="dropdown-item" href="{{ url_for('orders.print_order', order_id=o.id, copy='both', auto=1) }}" target="_blank" rel="noopener">
                  <i class="bi bi-files text-secondary"></i> Both Bills
                </a>
              </li>

              <li><hr class="dropdown-divider"></li>

              {% if o.balance_due > 0.01 %}
              <li>
                <a class="dropdown-item fw-semibold text-success" href="{{ url_for('billing.invoice', order_id=o.id) }}">
                  <i class="bi bi-cash-coin"></i> Receive Payment
                  <span class="badge bg-danger ms-1">{{ o.balance_due | money }}</span>
                </a>
              </li>
              {% endif %}

              {% if o.status == 'approved' and o.balance_due <= 0.01 %}
              <li>
                <a class="dropdown-item" href="{{ url_for('reports.order_pdf', order_id=o.id) }}">
                  <i class="bi bi-file-earmark-medical text-primary"></i> Report PDF
                </a>
              </li>
              <li>
                <a class="dropdown-item" href="{{ url_for('reports.view_pdf', order_id=o.id) }}" target="_blank" rel="noopener">
                  <i class="bi bi-eye text-primary"></i> Preview Report
                </a>
              </li>
              {% elif o.balance_due > 0.01 %}
              <li>
                <span class="dropdown-item text-muted disabled">
                  <i class="bi bi-lock-fill"></i> Report PDF
                  <span class="small ms-1">(balance due)</span>
                </span>
              </li>
              {% endif %}

              {% if o.status != 'cancelled' and o.has_any_results and not o.edit_unlocked and current_user.role == 'admin' %}
              <li>
                <form method="POST" action="{{ url_for('orders.unlock_order', order_id=o.id) }}" class="d-inline">
                  <button type="submit" class="dropdown-item">
                    <i class="bi bi-unlock-fill text-warning"></i> Unlock for Edit
                  </button>
                </form>
              </li>
              {% endif %}

              {% if o.status == 'cancelled' and current_user.role == 'admin' %}
              <li>
                <form method="POST" action="{{ url_for('orders.un_cancel_order', order_id=o.id) }}" class="d-inline"
                      onsubmit="return confirm('Restore this cancelled order? Any refund will be reversed.');">
                  <button type="submit" class="dropdown-item text-success">
                    <i class="bi bi-arrow-counterclockwise"></i> Un-cancel Order
                  </button>
                </form>
              </li>
              {% endif %}

              {% if o.status not in ['cancelled', 'approved'] %}
              <li><hr class="dropdown-divider"></li>
              <li>
                <a class="dropdown-item text-danger fw-semibold" href="#"
                   onclick="openCancelModal(event, {{ o.id }}, '{{ o.order_code }}', '{{ o.patient.full_name|e }}', {{ o.paid_amount or 0 }});">
                  <i class="bi bi-x-circle"></i> Cancel Order
                </a>
              </li>
              {% endif %}

            </ul>
          </div>
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>

  {# ============ FOOTER SUMMARY ============ #}
  <div class="dl-summary">
    <div class="stat"><span class="label">Total Amount</span><span class="value">{{ stats.total_amount | money }}</span></div>
    <div class="stat"><span class="label">Discounted</span><span class="value danger">{{ stats.total_discount | money }}</span></div>
    <div class="stat"><span class="label">Net Amount</span><span class="value success">{{ stats.net_amount | money }}</span></div>
    <div class="stat"><span class="label">Received</span><span class="value">{{ stats.paid_amount | money }}</span></div>
    <div class="stat"><span class="label">Due Amount</span><span class="value danger">{{ stats.due_amount | money }}</span></div>
    <div class="stat"><span class="label">No. of Cases</span><span class="value">{{ stats.case_count }}</span></div>
  </div>
  {% else %}
  <div class="dl-empty" style="border:1.5px solid #212529; background:#fafbfc;">
    <i class="bi bi-inbox fs-3 d-block mb-2"></i>
    No registrations in this range.
    <div class="small mt-1">Try adjusting the date range or filters above.</div>
  </div>
  {% endif %}

</div>

{# ============ CANCEL ORDER MODAL ============ #}
<div class="modal fade" id="cancelOrderModal" tabindex="-1">
  <div class="modal-dialog">
    <form method="POST" id="cancelOrderForm">
      <div class="modal-content" style="border-radius:0;">
        <div class="modal-header">
          <h5 class="modal-title"><i class="bi bi-x-circle text-danger"></i> Cancel Order</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <p class="mb-2"><strong id="cancelOrderLabel"></strong></p>
          <div class="alert alert-warning small py-2">
            <i class="bi bi-arrow-return-left"></i>
            <strong>Auto-refund:</strong>
            <span id="cancelRefundAmount" class="fw-bold">Rs 0</span>
            will be returned to the patient and deducted from today's Cash Summary automatically.
          </div>
          <div class="mb-2">
            <label class="form-label fw-semibold">Reason for cancellation <span class="text-danger">*</span></label>
            <textarea name="reason" class="form-control" rows="3" required
                      placeholder="e.g. Patient refused, sample hemolyzed..."></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Keep Order</button>
          <button type="submit" class="btn btn-danger"><i class="bi bi-x-circle"></i> Confirm Cancellation</button>
        </div>
      </div>
    </form>
  </div>
</div>
{% endblock %}

{% block scripts %}
<script>
function openCancelModal(event, orderId, orderCode, patientName, paidAmount) {
  event.preventDefault();
  var form = document.getElementById('cancelOrderForm');
  form.action = '/orders/' + orderId + '/cancel';
  document.getElementById('cancelOrderLabel').textContent = 'Lab # ' + orderCode + ' — ' + patientName;
  var cur = '{{ config.currency_symbol if config else \"Rs\" }}';
  document.getElementById('cancelRefundAmount').textContent = cur + ' ' + Number(paidAmount || 0).toFixed(2);
  var modal = new bootstrap.Modal(document.getElementById('cancelOrderModal'));
  modal.show();
}
</script>
{% endblock %}
"""

open(p, 'w', encoding='utf-8').write(t)
print('OK  - list.html rewritten (dense classical)')

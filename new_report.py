content = """{% extends 'base.html' %}
{% block title %}Cash Summary Report - {{ date_from }} to {{ date_to }}{% endblock %}

{% block content %}
<div class="csr-page">

  {# ============ HEADER BAR ============ #}
  <div class="csr-header">
    <div>
      <h1 class="csr-title">Cash Summary Report</h1>
      <div class="csr-subtitle">{{ date_from }} to {{ date_to }}</div>
    </div>
    <div class="csr-actions d-print-none">
      <button class="csr-btn csr-btn-primary" onclick="window.print()">
        Print
      </button>
      <a href="/billing/" class="csr-btn">Close</a>
    </div>
  </div>

  {# ============ KPI ROW ============ #}
  <table class="csr-kpi">
    <tr>
      <td>
        <div class="csr-kpi-label">Total Billed</div>
        <div class="csr-kpi-value">{{ stats.total_billed | money }}</div>
      </td>
      <td>
        <div class="csr-kpi-label">Collected</div>
        <div class="csr-kpi-value csr-success">{{ stats.total_collected | money }}</div>
      </td>
      <td>
        <div class="csr-kpi-label">Outstanding</div>
        <div class="csr-kpi-value csr-danger">{{ stats.outstanding | money }}</div>
      </td>
      <td>
        <div class="csr-kpi-label">Orders</div>
        <div class="csr-kpi-value">{{ stats.total_orders }}</div>
      </td>
    </tr>
  </table>

  {# ============ MAIN TABLE ============ #}
  <table class="csr-table">
    <thead>
      <tr>
        <th style="width: 110px;">Invoice</th>
        <th style="width: 80px;">Date</th>
        <th>Patient</th>
        <th style="width: 100px;">Patient #</th>
        <th class="num" style="width: 80px;">Total</th>
        <th class="num" style="width: 80px;">Discount</th>
        <th class="num" style="width: 80px;">Net</th>
        <th class="num" style="width: 80px;">Paid</th>
        <th class="num" style="width: 80px;">Balance</th>
        <th style="width: 80px;">Status</th>
      </tr>
    </thead>
    <tbody>
      {% for o in orders %}
      <tr class="{% if o.status == 'cancelled' %}row-cancelled{% endif %}">
        <td><a href="/orders/{{ o.id }}" class="csr-link">INV-{{ o.order_code }}</a></td>
        <td class="muted">{{ o.created_at | localtime('%d/%m/%y') }}</td>
        <td class="fw-semibold">{{ o.patient.full_name }}</td>
        <td class="muted">{{ o.patient.patient_code }}</td>
        <td class="num {% if o.status == 'cancelled' %}strike{% endif %}">{{ o.subtotal | money }}</td>
        <td class="num {% if o.status == 'cancelled' %}strike{% endif %}">{{ o.discount_value | money }}</td>
        <td class="num fw-semibold {% if o.status == 'cancelled' %}strike{% endif %}">{{ o.final_total | money }}</td>
        <td class="num csr-success">
          {%- if o.status == 'cancelled' -%}
            <span class="strike">refunded</span>
          {%- else -%}
            {{ o.paid_amount | money }}
          {%- endif -%}
        </td>
        <td class="num csr-danger">
          {%- if o.status == 'cancelled' -%}
            &mdash;
          {%- else -%}
            {{ o.balance_due | money }}
          {%- endif -%}
        </td>
        <td>
          {%- if o.status == 'cancelled' -%}
            <span class="badge-grey">CANCELLED</span>
          {%- elif o.payment_status == 'paid' -%}
            <span class="badge-green">PAID</span>
          {%- elif o.payment_status == 'partial' -%}
            <span class="badge-amber">PARTIAL</span>
          {%- else -%}
            <span class="badge-red">UNPAID</span>
          {%- endif -%}
        </td>
      </tr>
      {% else %}
      <tr>
        <td colspan="10" class="csr-empty">No orders in this date range.</td>
      </tr>
      {% endfor %}
    </tbody>
    <tfoot>
      <tr class="csr-tfoot">
        <td colspan="4" class="num">TOTALS</td>
        <td class="num">{{ stats.total_billed | money }}</td>
        <td></td>
        <td class="num fw-bold">{{ stats.total_billed | money }}</td>
        <td class="num fw-bold csr-success">{{ stats.total_collected | money }}</td>
        <td class="num fw-bold csr-danger">{{ stats.outstanding | money }}</td>
        <td></td>
      </tr>
    </tfoot>
  </table>

  <div class="csr-footer">
    Generated: {{ generated_at | localtime('%d-%b-%Y %I:%M %p') }}
  </div>

</div>

<style>
/* ============================================================
   Cash Summary Report - dense classical ledger layout
   ============================================================ */
.csr-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 16px 24px 40px;
  font-family: 'Segoe UI', Arial, sans-serif;
  font-size: 0.82rem;
  color: #212529;
}

/* Header */
.csr-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  border-bottom: 2px solid #212529;
  padding-bottom: 8px;
  margin-bottom: 12px;
}
.csr-title {
  font-size: 1.2rem;
  font-weight: 700;
  margin: 0;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}
.csr-subtitle {
  font-size: 0.78rem;
  color: #6c757d;
  margin-top: 2px;
  font-family: Consolas, Monaco, monospace;
}
.csr-actions {
  display: flex;
  gap: 6px;
}
.csr-btn {
  display: inline-block;
  padding: 5px 14px;
  font-size: 0.8rem;
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
.csr-btn:hover { background: #f1f3f5; color: #212529; }
.csr-btn-primary {
  background: #198754;
  border-color: #198754;
  color: #fff;
}
.csr-btn-primary:hover { background: #146c43; color: #fff; }

/* KPI strip */
.csr-kpi {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 12px;
  border: 1px solid #212529;
}
.csr-kpi td {
  border-right: 1px solid #212529;
  padding: 8px 14px;
  width: 25%;
  background: #f8f9fa;
}
.csr-kpi td:last-child { border-right: none; }
.csr-kpi-label {
  font-size: 0.66rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #6c757d;
  font-weight: 700;
  margin-bottom: 3px;
}
.csr-kpi-value {
  font-size: 1.15rem;
  font-weight: 700;
  font-family: Consolas, Monaco, monospace;
  font-variant-numeric: tabular-nums;
}
.csr-success { color: #146c43; }
.csr-danger  { color: #b02a37; }

/* Main table */
.csr-table {
  width: 100%;
  border-collapse: collapse;
  border: 1px solid #212529;
  font-size: 0.78rem;
}
.csr-table thead th {
  background: #212529;
  color: #fff;
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 6px 8px;
  text-align: left;
  border-right: 1px solid #495057;
  white-space: nowrap;
}
.csr-table thead th:last-child { border-right: none; }
.csr-table thead th.num { text-align: right; }

.csr-table tbody td {
  padding: 5px 8px;
  border-bottom: 1px solid #dee2e6;
  border-right: 1px solid #f1f3f5;
  vertical-align: middle;
}
.csr-table tbody td:last-child { border-right: none; }
.csr-table tbody tr:nth-child(even) { background: #fbfcfd; }
.csr-table tbody tr:hover { background: #f1f3f5; }
.csr-table tbody td.num {
  text-align: right;
  font-family: Consolas, Monaco, monospace;
  font-variant-numeric: tabular-nums;
}
.csr-table .muted { color: #6c757d; font-size: 0.74rem; }
.csr-table .fw-semibold { font-weight: 600; }
.csr-table .strike { text-decoration: line-through; color: #adb5bd; }

/* Row states */
.row-cancelled td {
  background: #f8f9fa !important;
  opacity: 0.8;
}

/* Footer row */
.csr-tfoot td {
  background: #e9ecef;
  font-weight: 700;
  border-top: 2px solid #212529;
  padding: 6px 8px;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}
.csr-tfoot td.num {
  text-align: right;
  font-family: Consolas, Monaco, monospace;
  text-transform: none;
  letter-spacing: 0;
  font-size: 0.82rem;
}

/* Badges */
.badge-green, .badge-red, .badge-amber, .badge-grey {
  display: inline-block;
  padding: 1px 6px;
  font-size: 0.64rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  border-radius: 0;
  color: #fff;
}
.badge-green { background: #198754; }
.badge-red   { background: #dc3545; }
.badge-amber { background: #ffc107; color: #664d03; }
.badge-grey  { background: #6c757d; }

.csr-link {
  color: #0d6efd;
  text-decoration: none;
  font-family: Consolas, Monaco, monospace;
  font-size: 0.76rem;
}
.csr-link:hover { text-decoration: underline; }

.csr-empty {
  padding: 32px !important;
  text-align: center;
  color: #6c757d;
  font-style: italic;
}

.csr-footer {
  margin-top: 12px;
  padding-top: 6px;
  border-top: 1px solid #dee2e6;
  font-size: 0.7rem;
  color: #6c757d;
  font-family: Consolas, Monaco, monospace;
  text-align: right;
}

/* ============================================================
   Print rules
   ============================================================ */
@media print {
  body { background: #fff !important; }
  .d-print-none, .csr-actions { display: none !important; }
  .csr-page { padding: 0; max-width: 100%; }
  .csr-table { font-size: 0.7rem; }
  .csr-table thead th {
    background: #212529 !important;
    color: #fff !important;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  .csr-kpi td { background: #f8f9fa !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .csr-tfoot td { background: #e9ecef !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .badge-green, .badge-red, .badge-amber, .badge-grey {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  .csr-page { page-break-inside: avoid; }
}
</style>
{% endblock %}
"""

path = 'modules/billing/templates/billing/report.html'
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('OK - report.html replaced with dense classical layout')

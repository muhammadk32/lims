"""
Cash Summary redesign:
- /billing/       -> simple page (just From/To + Report button)
- /billing/report -> full report, opens in new tab
"""
import os

# ============================================================
# 1. Replace billing/list.html with the simple launcher
# ============================================================
SIMPLE_LIST = """{% extends 'base.html' %}
{% block title %}Cash Summary — LabMS{% endblock %}

{% block content %}
<div class="container py-5" style="max-width: 760px;">

  <div class="text-center mb-4">
    <h3 class="fw-bold mb-1"><i class="bi bi-cash-coin text-primary"></i> Cash Summary</h3>
    <p class="text-muted small mb-0">Choose a date range and open the report in a new window</p>
  </div>

  <div class="card border-0 shadow-sm">
    <div class="card-body p-4">
      <form method="GET" action="{{ url_for('billing.report') }}" target="_blank">
        <div class="row g-3 align-items-end">
          <div class="col-md-5">
            <label class="form-label small fw-semibold text-uppercase text-muted">From date</label>
            <input type="date" name="date_from" class="form-control form-control-lg"
                   value="{{ default_from }}" required>
          </div>
          <div class="col-md-5">
            <label class="form-label small fw-semibold text-uppercase text-muted">To date</label>
            <input type="date" name="date_to" class="form-control form-control-lg"
                   value="{{ default_to }}" required>
          </div>
          <div class="col-md-2">
            <button type="submit" class="btn btn-primary btn-lg w-100">
              <i class="bi bi-file-earmark-bar-graph"></i> Report
            </button>
          </div>
        </div>

        <div class="mt-3 small text-muted">
          <i class="bi bi-info-circle"></i>
          The report opens in a new tab. You can print it or save as PDF from there.
        </div>
      </form>
    </div>
  </div>

  <div class="text-center mt-3">
    <a href="{{ url_for('billing.due_collection') }}" class="btn btn-outline-danger btn-sm">
      <i class="bi bi-cash-stack"></i> Due Collection
    </a>
    <a href="{{ url_for('billing.payments') }}" class="btn btn-outline-secondary btn-sm ms-2">
      <i class="bi bi-credit-card"></i> All Payments
    </a>
  </div>

</div>
{% endblock %}
"""

path = 'modules/billing/templates/billing/list.html'
with open(path, 'w', encoding='utf-8') as f:
    f.write(SIMPLE_LIST)
print('OK  - billing/list.html replaced with launcher')


# ============================================================
# 2. Create the full report template
# ============================================================
REPORT_HTML = """{% extends 'base.html' %}
{% block title %}Cash Summary Report — {{ date_from }} to {{ date_to }}{% endblock %}

{% block content %}
<div class="container-fluid py-4">

  <div class="d-flex justify-content-between align-items-center mb-3 d-print-none">
    <div>
      <h3 class="fw-bold mb-0"><i class="bi bi-file-earmark-bar-graph"></i> Cash Summary Report</h3>
      <p class="text-muted small mb-0">{{ date_from }} &rarr; {{ date_to }}</p>
    </div>
    <div class="d-flex gap-2">
      <button class="btn btn-primary" onclick="window.print()">
        <i class="bi bi-printer"></i> Print
      </button>
      <a href="{{ url_for('billing.index') }}" class="btn btn-outline-secondary">
        <i class="bi bi-x-lg"></i> Close
      </a>
    </div>
  </div>

  <div class="row g-3 mb-4">
    <div class="col-md-3">
      <div class="card border-0 shadow-sm">
        <div class="card-body">
          <div class="text-muted small text-uppercase">Total Billed</div>
          <div class="fs-4 fw-bold">{{ stats.total_billed | money }}</div>
        </div>
      </div>
    </div>
    <div class="col-md-3">
      <div class="card border-0 shadow-sm">
        <div class="card-body">
          <div class="text-muted small text-uppercase">Collected</div>
          <div class="fs-4 fw-bold text-success">{{ stats.total_collected | money }}</div>
        </div>
      </div>
    </div>
    <div class="col-md-3">
      <div class="card border-0 shadow-sm">
        <div class="card-body">
          <div class="text-muted small text-uppercase">Outstanding</div>
          <div class="fs-4 fw-bold text-danger">{{ stats.outstanding | money }}</div>
        </div>
      </div>
    </div>
    <div class="col-md-3">
      <div class="card border-0 shadow-sm">
        <div class="card-body">
          <div class="text-muted small text-uppercase">Orders</div>
          <div class="fs-4 fw-bold">{{ stats.total_orders }}</div>
        </div>
      </div>
    </div>
  </div>

  <div class="card border-0 shadow-sm">
    <div class="table-responsive">
      <table class="table table-hover align-middle mb-0">
        <thead class="table-light">
          <tr>
            <th>Invoice</th>
            <th>Date</th>
            <th>Patient</th>
            <th>Patient #</th>
            <th class="text-end">Total</th>
            <th class="text-end">Discount</th>
            <th class="text-end">Net</th>
            <th class="text-end">Paid</th>
            <th class="text-end">Balance</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {% for o in orders %}
          <tr class="{% if o.status == 'cancelled' %}cancelled-row{% endif %}">
            <td><a href="{{ url_for('orders.view_order', order_id=o.id) }}" class="text-decoration-none"><code>INV-{{ o.order_code }}</code></a></td>
            <td class="text-muted small">{{ o.created_at | localtime('%d/%m/%y') }}</td>
            <td>
              <div class="fw-semibold">{{ o.patient.full_name }}</div>
            </td>
            <td><code>{{ o.patient.patient_code }}</code></td>
            <td class="text-end {% if o.status == 'cancelled' %}strike-cancelled{% endif %}">{{ o.subtotal | money }}</td>
            <td class="text-end {% if o.status == 'cancelled' %}strike-cancelled{% endif %}">{{ o.discount_value | money }}</td>
            <td class="text-end fw-semibold {% if o.status == 'cancelled' %}strike-cancelled{% endif %}">{{ o.final_total | money }}</td>
            <td class="text-end text-success">
              {% if o.status == 'cancelled' %}
                <span class="refund-pill">refunded</span>
              {% else %}
                {{ o.paid_amount | money }}
              {% endif %}
            </td>
            <td class="text-end text-danger">
              {% if o.status == 'cancelled' %}—{% else %}{{ o.balance_due | money }}{% endif %}
            </td>
            <td>
              {% if o.status == 'cancelled' %}
                <span class="cancelled-badge">Cancelled</span>
              {% elif o.payment_status == 'paid' %}
                <span class="badge bg-success">Paid</span>
              {% elif o.payment_status == 'partial' %}
                <span class="badge bg-warning text-dark">Partial</span>
              {% else %}
                <span class="badge bg-danger">Unpaid</span>
              {% endif %}
            </td>
          </tr>
          {% else %}
          <tr>
            <td colspan="10" class="text-center text-muted py-5">
              <i class="bi bi-inbox fs-2 d-block mb-2"></i>
              No orders in this date range.
            </td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  </div>

  <div class="text-center text-muted small mt-4">
    Generated on {{ generated_at | localtime('%d-%b-%Y %I:%M %p') }}
  </div>

</div>

<style>
.cancelled-row td { background: #f8f9fa !important; opacity: 0.75; }
.strike-cancelled { text-decoration: line-through; color: #adb5bd !important; }
.cancelled-badge { display:inline-block; background:#6c757d; color:#fff; font-size:0.68rem; font-weight:700; padding:2px 7px; border-radius:3px; }
.refund-pill { color: #b02a37; font-weight: 700; font-size: 0.72rem; font-style: italic; }

@media print {
  .d-print-none { display: none !important; }
  .card { border: 1px solid #dee2e6 !important; box-shadow: none !important; }
  .btn { display: none !important; }
  body { font-size: 0.82rem; }
  .container-fluid { padding: 0 !important; }
}
</style>
{% endblock %}
"""

path = 'modules/billing/templates/billing/report.html'
with open(path, 'w', encoding='utf-8') as f:
    f.write(REPORT_HTML)
print('OK  - billing/report.html created')


# ============================================================
# 3. Patch billing/routes.py — update index + add report route
# ============================================================
rp = 'modules/billing/routes.py'
r = open(rp, encoding='utf-8').read()

# 3a. Update index() to pass default dates
old_idx = """    orders, stats = q.list_billing_orders(q=search, filter_by=filter_by)

    return render_template(
        'billing/list.html',
        orders=orders,
        stats=stats,
        q=search,
        filter_by=filter_by,
    )"""

new_idx = """    from datetime import date as _date
    today = _date.today()
    first_of_month = today.replace(day=1)

    return render_template(
        'billing/list.html',
        default_from=first_of_month.strftime('%Y-%m-%d'),
        default_to=today.strftime('%Y-%m-%d'),
    )"""

if old_idx in r:
    r = r.replace(old_idx, new_idx, 1)
    print('OK  - routes.py: index() simplified')
else:
    print('WARN - routes.py: index() block pattern not found')

# 3b. Add report route after the index function
anchor = "# ---------- Invoice View (HTML) ----------"
new_route = """# ---------- Cash Summary Report ----------
@billing_bp.route('/report')
@login_required
@permission_required('view_billing')
def report():
    \"\"\"Full cash summary report for a date range — opens in new tab.\"\"\"
    from datetime import datetime as _dt, date as _date

    date_from_str = request.args.get('date_from', '').strip()
    date_to_str = request.args.get('date_to', '').strip()

    # Defaults: this month
    today = _date.today()
    try:
        date_from = _dt.strptime(date_from_str, '%Y-%m-%d').date() if date_from_str else today.replace(day=1)
    except (ValueError, TypeError):
        date_from = today.replace(day=1)
    try:
        date_to = _dt.strptime(date_to_str, '%Y-%m-%d').date() if date_to_str else today
    except (ValueError, TypeError):
        date_to = today

    orders, stats = q.list_billing_orders_for_range(date_from, date_to)

    return render_template(
        'billing/report.html',
        orders=orders,
        stats=stats,
        date_from=date_from.strftime('%d-%b-%Y'),
        date_to=date_to.strftime('%d-%b-%Y'),
        generated_at=__import__('datetime').datetime.now(),
    )


"""
if 'def report():' not in r and anchor in r:
    r = r.replace(anchor, new_route + anchor, 1)
    print('OK  - routes.py: /report route added')
elif 'def report():' in r:
    print('SKIP - routes.py already has report()')
else:
    print('WARN - routes.py: anchor not found, appending at end')
    r += '\n\n' + new_route

open(rp, 'w', encoding='utf-8').write(r)


# ============================================================
# 4. Patch billing/queries.py — add list_billing_orders_for_range
# ============================================================
qp = 'modules/billing/queries.py'
qq = open(qp, encoding='utf-8').read()

if 'list_billing_orders_for_range' not in qq:
    new_q = """

# ============================================================
# Range-based report query
# ============================================================
def list_billing_orders_for_range(date_from, date_to):
    \"\"\"Return (orders, stats) for a date range — used by /billing/report.\"\"\"
    from modules.orders.models import Order
    from sqlalchemy import func

    orders = (
        Order.query
        .filter(func.date(Order.created_at) >= date_from)
        .filter(func.date(Order.created_at) <= date_to)
        .order_by(Order.id.desc())
        .all()
    )

    total_billed = round(sum(o.final_total for o in orders if o.status != 'cancelled'), 2)
    total_collected = round(sum(o.paid_amount for o in orders), 2)
    outstanding = round(sum(o.balance_due for o in orders if o.status != 'cancelled'), 2)
    active_count = sum(1 for o in orders if o.status != 'cancelled')

    stats = {
        'total_billed': total_billed,
        'total_collected': total_collected,
        'outstanding': outstanding,
        'total_orders': active_count,
    }
    return orders, stats
"""
    qq += new_q
    open(qp, 'w', encoding='utf-8').write(qq)
    print('OK  - queries.py: list_billing_orders_for_range added')
else:
    print('SKIP - queries.py already has the range function')


print()
print('=' * 55)
print('Done. Restart Flask and test:')
print('  /billing/          -> date picker + Report button')
print('  Click Report       -> opens /billing/report in new tab')
print('=' * 55)

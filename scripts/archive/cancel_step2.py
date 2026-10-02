"""
Add Cancel Order to Ledger dropdown + modal + JS.
"""
path = 'modules/orders/templates/orders/list.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

if 'cancelOrderModal' in html:
    print('SKIP - cancel modal already present')
    raise SystemExit(0)

# ---------- 1. Insert Cancel item before dropdown </ul> ----------
# Anchor: the unique block around the last </ul>
anchor = """                {% endif %}

</ul>
            </div>
          </td>"""

cancel_item = """                {% endif %}

                {% if o.status not in ['cancelled', 'approved'] %}
                <li><hr class="dropdown-divider"></li>
                <li>
                  <a class="dropdown-item text-danger fw-semibold"
                     href="#"
                     onclick="openCancelModal(event, {{ o.id }}, '{{ o.order_code }}', '{{ o.patient.full_name|e }}', {{ o.paid_amount or 0 }});">
                    <i class="bi bi-x-circle me-2"></i> Cancel Order
                  </a>
                </li>
                {% endif %}

</ul>
            </div>
          </td>"""

if anchor not in html:
    print('ERR - dropdown anchor not found')
    raise SystemExit(1)

html = html.replace(anchor, cancel_item, 1)
print('OK  - Cancel item added to dropdown')

# ---------- 2. Insert modal + JS before final {% endblock %} ----------
# Find the LAST {% endblock %}
last_end = html.rfind('{% endblock %}')
if last_end == -1:
    print('ERR - no {% endblock %} found')
    raise SystemExit(1)

modal = """

{# ============================================================
   Cancel Order Modal (shared — used by all rows)
   ============================================================ #}
<div class="modal fade" id="cancelOrderModal" tabindex="-1">
  <div class="modal-dialog">
    <form method="POST" id="cancelOrderForm">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            <i class="bi bi-x-circle text-danger"></i> Cancel Order
          </h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <p class="mb-2">
            <strong id="cancelOrderLabel"></strong>
          </p>
          <div class="alert alert-warning small py-2">
            <i class="bi bi-arrow-return-left"></i>
            <strong>Auto-refund:</strong>
            <span id="cancelRefundAmount" class="fw-bold">Rs 0</span>
            will be returned to the patient and deducted from today's
            Cash Summary automatically.
          </div>
          <div class="mb-2">
            <label class="form-label fw-semibold">
              Reason for cancellation <span class="text-danger">*</span>
            </label>
            <textarea name="reason" class="form-control" rows="3" required
                      placeholder="e.g. Patient refused, sample hemolyzed, test not available..."></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-outline-secondary"
                  data-bs-dismiss="modal">Keep Order</button>
          <button type="submit" class="btn btn-danger">
            <i class="bi bi-x-circle"></i> Confirm Cancellation
          </button>
        </div>
      </div>
    </form>
  </div>
</div>

<script>
function openCancelModal(event, orderId, orderCode, patientName, paidAmount) {
  event.preventDefault();
  var form = document.getElementById('cancelOrderForm');
  form.action = '/orders/' + orderId + '/cancel';
  document.getElementById('cancelOrderLabel').textContent =
    'Lab # ' + orderCode + ' \\u2014 ' + patientName;
  var cur = '{{ config.currency_symbol }}';
  document.getElementById('cancelRefundAmount').textContent =
    cur + ' ' + Number(paidAmount || 0).toFixed(2);
  var modal = new bootstrap.Modal(document.getElementById('cancelOrderModal'));
  modal.show();
}
</script>
"""

html = html[:last_end] + modal + "\n" + html[last_end:]

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)

print('OK  - Modal + JS added')
print()
print('=' * 55)
print('Done. Restart Flask and test:')
print('  /orders/ -> click eye icon -> Cancel Order')
print('=' * 55)

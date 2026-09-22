"""
Add Receive Payment + Report PDF to the Ledger dropdown.
"""
path = 'modules/orders/templates/orders/list.html'

with open(path, 'r', encoding='utf-8') as f:
    src = f.read()

anchor = '<ul class="dropdown-menu dropdown-menu-end ledger-actions-menu">'
idx = src.find(anchor)
if idx == -1:
    print('ERROR: dropdown <ul> not found')
    raise SystemExit(1)

close_idx = src.find('</ul>', idx)
if close_idx == -1:
    print('ERROR: closing </ul> not found')
    raise SystemExit(1)

# Guard against double-run
if 'Receive Payment' in src:
    print('SKIP: dropdown already has Receive Payment')
    raise SystemExit(0)

insert = '''                <li><hr class="dropdown-divider"></li>

                {% if o.balance_due > 0.01 %}
                <li>
                  <a class="dropdown-item fw-semibold text-success"
                     href="{{ url_for(\'billing.invoice\', order_id=o.id) }}">
                    <i class="bi bi-cash-coin me-2"></i> Receive Payment
                    <span class="badge bg-danger ms-1">Rs {{ \'%.0f\'|format(o.balance_due) }}</span>
                  </a>
                </li>
                {% endif %}

                {% if o.status == \'approved\' and o.balance_due <= 0.01 %}
                <li>
                  <a class="dropdown-item"
                     href="{{ url_for(\'reports.order_pdf\', order_id=o.id) }}">
                    <i class="bi bi-file-earmark-medical me-2 text-primary"></i> Report PDF
                  </a>
                </li>
                <li>
                  <a class="dropdown-item"
                     href="{{ url_for(\'reports.view_pdf\', order_id=o.id) }}"
                     target="_blank" rel="noopener">
                    <i class="bi bi-eye me-2 text-primary"></i> Preview Report
                  </a>
                </li>
                {% elif o.balance_due > 0.01 %}
                <li>
                  <span class="dropdown-item text-muted disabled" title="Clear balance first">
                    <i class="bi bi-lock-fill me-2"></i> Report PDF
                    <span class="small ms-2">(balance due)</span>
                  </span>
                </li>
                {% endif %}

'''

src = src[:close_idx] + insert + src[close_idx:]

with open(path, 'w', encoding='utf-8') as f:
    f.write(src)

print('OK - dropdown updated')

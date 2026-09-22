"""
Ledger row display for cancelled orders:
- strike-through money values
- Due shows 0
- Payment column shows CANCELLED badge
- Show refund amount in Paid column if any was refunded
"""
path = 'modules/orders/templates/orders/list.html'
html = open(path, encoding='utf-8').read()

if 'cancelled-display' in html:
    print('SKIP - already patched')
    raise SystemExit(0)

# Add CSS block if not present
if '.strike-cancelled' not in html:
    css_anchor = '<style>'
    css_add = '''<style>
.cancelled-row td { background: #f8f9fa !important; }
.strike-cancelled {
  text-decoration: line-through;
  color: #adb5bd !important;
}
.cancelled-badge {
  display: inline-block;
  background: #6c757d; color: #fff;
  font-size: 0.66rem; font-weight: 700;
  padding: 2px 7px; border-radius: 3px;
  letter-spacing: 0.05em;
}
.refund-pill {
  color: #b02a37; font-weight: 700;
  font-size: 0.78rem;
}
'''
    html = html.replace(css_anchor, css_add, 1)
    print('OK  - CSS added')
else:
    print('SKIP - CSS already present')

# Patch the money cells to strike-through when cancelled
# Total cell
replacements = [
    # Total
    (
        '<td class="text-end">{{ config.currency_symbol }} {{ \'%.2f\'|format(o.subtotal) }}</td>',
        '<td class="text-end {% if o.status == \'cancelled\' %}strike-cancelled{% endif %}">{{ config.currency_symbol }} {{ \'%.2f\'|format(o.subtotal) }}</td>'
    ),
    # Discount
    (
        '<td class="text-end text-danger">−{{ config.currency_symbol }} {{ \'%.2f\'|format(o.discount_value) }}</td>',
        '<td class="text-end text-danger {% if o.status == \'cancelled\' %}strike-cancelled{% endif %}">−{{ config.currency_symbol }} {{ \'%.2f\'|format(o.discount_value) }}</td>'
    ),
    # Net
    (
        '<td class="text-end fw-semibold">{{ config.currency_symbol }} {{ \'%.2f\'|format(o.final_total) }}</td>',
        '<td class="text-end fw-semibold {% if o.status == \'cancelled\' %}strike-cancelled{% endif %}">{{ config.currency_symbol }} {{ \'%.2f\'|format(o.final_total) }}</td>'
    ),
]

matches = 0
for old, new in replacements:
    if old in html:
        html = html.replace(old, new, 1)
        matches += 1
print(f'OK  - {matches}/3 money cells patched')

open(path, 'w', encoding='utf-8').write(html)

print()
print('NOTE: this script only did the strike-through part.')
print('The Due=0 and Payment badge fixes need one more step.')
print('Run the diagnostic to see the remaining cells.')

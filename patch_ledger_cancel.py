"""
Final ledger-cancelled patch — self-contained, pattern-based.
"""
import re

path = 'modules/orders/templates/orders/list.html'
html = open(path, encoding='utf-8').read()
original = html

# ---------- 1. Add cancelled-row class to the <tr> ----------
if '<tr class="order-row' not in html and '<tr>' in html:
    # Match the row inside the for loop
    html = html.replace(
        '        {% for o in orders %}\n        <tr>',
        '        {% for o in orders %}\n        <tr class="order-row {% if o.status == \'cancelled\' %}cancelled-row{% endif %}">',
        1,
    )
    if '<tr class="order-row' in html:
        print('OK  - <tr> cancelled-row class added')

# ---------- 2. Fix discount cell (multi-line) ----------
# Find the block between the Total cell and the Net cell
discount_pattern = re.compile(
    r'(<td class="text-end text-danger">)(\s*\{%\s*if\s+o\.discount_value\s*>\s*0\s*%\})',
    re.DOTALL,
)
if 'strike-cancelled' not in html.split('text-end text-danger')[1][:200]:
    html = discount_pattern.sub(
        r'<td class="text-end text-danger {% if o.status == \'cancelled\' %}strike-cancelled{% endif %}">\2',
        html,
        count=1,
    )
    print('OK  - Discount cell patched')

# ---------- 3. Force Due = 0 when cancelled ----------
# Match the Due cell
due_pattern = re.compile(
    r'<td class="text-end[^"]*">\s*\{\{\s*config\.currency_symbol\s*\}\}\s*\{\{\s*\'%\.2f\'\s*\|\s*format\(o\.balance_due\)\s*\}\}\s*</td>',
    re.DOTALL,
)

def due_replacement(m):
    return (
        '<td class="text-end">'
        "{% if o.status == 'cancelled' %}"
        '—'
        '{% else %}'
        "{{ config.currency_symbol }} {{ '%.2f'|format(o.balance_due) }}"
        '{% endif %}'
        '</td>'
    )

if 'o.balance_due' in html and "o.status == 'cancelled' %}}—" not in html:
    html_new = due_pattern.sub(due_replacement, html, count=1)
    if html_new != html:
        html = html_new
        print('OK  - Due cell forced to dash when cancelled')

# ---------- 4. Force Paid to dash when cancelled ----------
paid_pattern = re.compile(
    r'<td class="text-end[^"]*">\s*\{\{\s*config\.currency_symbol\s*\}\}\s*\{\{\s*\'%\.2f\'\s*\|\s*format\(o\.paid_amount\)\s*\}\}\s*</td>',
    re.DOTALL,
)

def paid_replacement(m):
    return (
        '<td class="text-end">'
        "{% if o.status == 'cancelled' %}"
        '<span class="refund-pill">refunded</span>'
        '{% else %}'
        "{{ config.currency_symbol }} {{ '%.2f'|format(o.paid_amount) }}"
        '{% endif %}'
        '</td>'
    )

if 'o.paid_amount' in html:
    html_new = paid_pattern.sub(paid_replacement, html, count=1)
    if html_new != html:
        html = html_new
        print('OK  - Paid cell shows refund marker when cancelled')

# ---------- 5. Payment badge → grey "Cancelled" ----------
# The badge likely uses pay-pill with text like 'Paid' / 'Unpaid' / 'Partial'
badge_pattern = re.compile(
    r'(<span class="pay-pill\s+\{\{\s*o\.payment_status\s*\}\}">)([^<]*)(</span>)',
    re.DOTALL,
)
if badge_pattern.search(html):
    def badge_replacement(m):
        return (
            "{% if o.status == 'cancelled' %}"
            '<span class="cancelled-badge">Cancelled</span>'
            '{% else %}'
            + m.group(1) + m.group(2) + m.group(3) +
            '{% endif %}'
        )
    html = badge_pattern.sub(badge_replacement, html, count=1)
    print('OK  - Payment badge shows Cancelled')

# ---------- 6. Add refund amount next to cancelled badge if any paid ----------
# (Optional — only if we have a refunded_at column)
if 'refund-pill' not in html:
    css_add = '''
.refund-pill {
  color: #b02a37; font-weight: 700;
  font-size: 0.7rem;
  font-style: italic;
}
'''
    html = html.replace('<style>', '<style>' + css_add, 1)
    print('OK  - .refund-pill CSS added')

# ---------- Save ----------
if html != original:
    open(path, 'w', encoding='utf-8').write(html)
    print()
    print('Saved changes to list.html')
else:
    print()
    print('No changes — patterns did not match, or already applied')

print()
print('=' * 50)
print('Restart Flask and open /orders/ to see result.')
print('=' * 50)

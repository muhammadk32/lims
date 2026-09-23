# 1. Discount without minus sign in rows
# 2. Remove redundant TOTAL row
p = 'modules/analytics/templates/analytics/commission_detail.html'
s = open(p, encoding='utf-8').read()

# ---- 1. Remove minus sign from discount cells ----
# Row cell
s = s.replace(
    '<td class="num text-danger">{% if r.discount > 0 %}−{{ r.discount | money }}{% else %}—{% endif %}</td>',
    '<td class="num text-danger">{% if r.discount > 0 %}{{ r.discount | money }}{% else %}—{% endif %}</td>',
    1,
)

# ---- 2. Remove the redundant TOTAL footer row ----
import re
# The old TOTAL footer (with 2,209 / -545)
s = re.sub(
    r'<tfoot>\s*<tr>\s*<td colspan="4">TOTAL</td>.*?</tr>\s*</tfoot>\s*',
    '',
    s,
    count=1,
    flags=re.DOTALL,
)

open(p, 'w', encoding='utf-8').write(s)
print('OK  - discount minus removed')
print('OK  - redundant TOTAL row removed')

# Verify
s2 = open(p, encoding='utf-8').read()
print()
print('Verify:')
print('  old TOTAL row gone:', '<td colspan="4">TOTAL</td>' not in s2)
print('  TOTAL SHARE row present:', 'Total Share for' in s2 or 'TOTAL SHARE' in s2)
print('  discount minus removed:', '−{{ r.discount' not in s2)

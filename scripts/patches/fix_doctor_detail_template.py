# Remove commission column from doctor_detail.html
p = 'modules/analytics/templates/analytics/doctor_detail.html'
s = open(p, encoding='utf-8').read()

# 1. Remove commission th (header)
s = s.replace('      <th class="num">Commission</th>\n', '', 1)
s = s.replace('<th class="num">Commission</th>\n      ', '', 1)
s = s.replace('\n      <th class="num">Commission</th>', '', 1)

# 2. Remove body cell
import re
s = re.sub(
    r'<td class="num fw-semibold">\{% if r\.commission.*?</td>\s*\n',
    '',
    s,
    flags=re.DOTALL,
)

# 3. Remove footer cell
s = re.sub(
    r'<td class="num">\{\{ totals\.commission \| money \}\}</td>\s*\n',
    '',
    s,
    flags=re.DOTALL,
)

open(p, 'w', encoding='utf-8').write(s)

# Verify
s2 = open(p, encoding='utf-8').read()
print('commission header gone:', '<th class="num">Commission</th>' not in s2)
print('r.commission refs gone:', 'r.commission' not in s2)
print('totals.commission refs gone:', 'totals.commission' not in s2)

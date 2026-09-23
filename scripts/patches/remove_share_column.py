# Remove Share column from every row. Keep only the total.
p = 'modules/analytics/templates/analytics/commission_detail.html'
s = open(p, encoding='utf-8').read()

import re

# 1. Remove the header <th>
s = s.replace('<th class="num" style="width: 100px;">Share</th>\n', '', 1)
s = re.sub(r'<th[^>]*>Share</th>\s*\n', '', s, count=1)

# 2. Remove per-row share cell (however it's currently written)
s = re.sub(
    r'<td class="num fw-semibold"[^>]*>.*?</td>\s*\n',
    '',
    s,
    count=1,
    flags=re.DOTALL,
)

# 3. Remove the per-row share cell from the TOTAL footer row
s = re.sub(
    r'<td class="num">\{\{ totals\.commission \| money \}\}</td>\s*\n',
    '',
    s,
    count=1,
)

# 4. Fix colspan of empty state (was 7 now 6)
s = s.replace('colspan="7"', 'colspan="6"', 1)

# 5. Add a clean total footer row at the bottom of the table
if 'TOTAL SHARE' not in s:
    # Insert before the closing </table>
    idx = s.rfind('</table>')
    footer = '''
  <tfoot>
    <tr>
      <td colspan="6" style="text-align:right; padding-right:12px; font-weight:700; text-transform:uppercase; letter-spacing:0.04em;">
        Total Share for {{ referral_name }}
      </td>
      <td class="num" style="font-size:1.05rem; font-weight:800;">
        {{ totals.commission | money }}
      </td>
    </tr>
  </tfoot>
'''
    s = s[:idx] + footer + s[idx:]
    print('OK  - Total Share footer added')

open(p, 'w', encoding='utf-8').write(s)
print('OK  - Share column removed from rows')

# Verify
s2 = open(p, encoding='utf-8').read()
print()
print('Verification:')
print('  Header "Share" removed:', '<th' not in s2.split('TOTAL SHARE')[0].split('<thead>')[1][-300:] if '<thead>' in s2 else 'unknown')
print('  "TOTAL SHARE" present:', 'TOTAL SHARE' in s2)

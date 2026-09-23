# Add per-column TOTAL row back to commission detail table
p = 'modules/analytics/templates/analytics/commission_detail.html'
s = open(p, encoding='utf-8').read()

# Remove existing tfoot (whatever is there now)
import re
s = re.sub(r'<tfoot>.*?</tfoot>\s*', '', s, count=1, flags=re.DOTALL)

# Insert a clean 2-row footer before </table>
idx = s.rfind('</table>')

footer = '''  <tfoot>
    <tr>
      <td colspan="4" style="text-align:right; font-weight:700; text-transform:uppercase; letter-spacing:0.04em; padding-right:12px; border-top:2px solid #212529;">
        TOTAL
      </td>
      <td class="num" style="font-weight:700; border-top:2px solid #212529;">
        {{ totals.net | money }}
      </td>
      <td class="num" style="font-weight:700; border-top:2px solid #212529;">
        {{ totals.discount | money }}
      </td>
    </tr>
    <tr>
      <td colspan="4" style="text-align:right; font-weight:700; text-transform:uppercase; letter-spacing:0.04em; padding-right:12px;">
        TOTAL SHARE FOR {{ referral_name }}
      </td>
      <td colspan="2" class="num" style="font-size:1.05rem; font-weight:800; color:#198754;">
        {{ totals.commission | money }}
      </td>
    </tr>
  </tfoot>
'''
s = s[:idx] + footer + s[idx:]

open(p, 'w', encoding='utf-8').write(s)
print('OK  - per-column TOTAL row + Total Share row added')

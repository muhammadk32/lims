# Restructure commission_detail table columns
p = 'modules/analytics/templates/analytics/commission_detail.html'
s = open(p, encoding='utf-8').read()

# Find table start and end
import re
tbl_start = s.find('<table class="an-table">')
tbl_end = s.find('</table>', tbl_start) + len('</table>')

new_table = '''<table class="an-table">
  <thead>
    <tr>
      <th style="width: 110px;">Date</th>
      <th style="width: 110px;">Invoice #</th>
      <th style="width: 18%;">Patient Name</th>
      <th>Test Details</th>
      <th class="num" style="width: 100px;">Sub Total</th>
      <th class="num" style="width: 100px;">Discount</th>
      <th class="num" style="width: 100px;">Total Net</th>
    </tr>
  </thead>
  <tbody>
    {% for r in rows %}
    <tr>
      <td class="muted">{{ r.date | localtime('%d/%m/%y %H:%M') }}</td>
      <td><a href="/orders/{{ r.order_id }}" class="text-decoration-none"><code>INV-{{ r.order_code }}</code></a></td>
      <td class="fw-semibold">{{ r.patient }}</td>
      <td class="muted" style="font-size: 0.76rem;">{{ r.tests_list }}</td>
      <td class="num">{{ r.subtotal | money }}</td>
      <td class="num text-danger">{% if r.discount > 0 %}{{ r.discount | money }}{% else %}—{% endif %}</td>
      <td class="num fw-semibold">{{ r.net | money }}</td>
    </tr>
    {% else %}
    <tr><td colspan="7" class="an-empty">No commission data for this referral in this range.</td></tr>
    {% endfor %}
  </tbody>
  <tfoot>
    <tr>
      <td colspan="4" style="text-align:right; font-weight:700; text-transform:uppercase; letter-spacing:0.04em; padding-right:12px; border-top:2px solid #212529;">
        TOTAL
      </td>
      <td class="num" style="font-weight:700; border-top:2px solid #212529;">
        {{ totals.subtotal | money }}
      </td>
      <td class="num" style="font-weight:700; border-top:2px solid #212529;">
        {{ totals.discount | money }}
      </td>
      <td class="num" style="font-weight:700; border-top:2px solid #212529;">
        {{ totals.net | money }}
      </td>
    </tr>
    <tr>
      <td colspan="6" style="text-align:right; font-weight:700; text-transform:uppercase; letter-spacing:0.04em; padding-right:12px;">
        TOTAL SHARE FOR {{ referral_name }}
      </td>
      <td class="num" style="font-size:1.05rem; font-weight:800; color:#198654;">
        {{ totals.commission | money }}
      </td>
    </tr>
  </tfoot>
</table>'''

s = s[:tbl_start] + new_table + s[tbl_end:]
open(p, 'w', encoding='utf-8').write(s)
print('OK - table restructured')

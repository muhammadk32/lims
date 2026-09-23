# Remove Status column from commission_detail.html
p = 'modules/analytics/templates/analytics/commission_detail.html'
s = open(p, encoding='utf-8').read()

# 1. Remove header <th>
s = s.replace('      <th style="width: 90px;">Status</th>\n', '', 1)

# 2. Remove the Status cell in the body
old_cell = '''      <td>
        {% if r.commission_paid %}
          <span class="badge-ok">PAID</span>
        {% else %}
          <span class="badge-abn">PENDING</span>
        {% endif %}
      </td>
'''
s = s.replace(old_cell, '', 1)

# 3. Remove trailing empty <td> in footer row
s = s.replace('      <td class="num">{{ totals.commission | money }}</td>\n      <td></td>\n',
              '      <td class="num">{{ totals.commission | money }}</td>\n', 1)

# 4. Fix colspan in empty-state row (was 8)
s = s.replace('colspan="8"', 'colspan="7"', 1)

open(p, 'w', encoding='utf-8').write(s)
print('OK  - Status column removed')

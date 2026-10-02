# Rename "Result" header to the current visit date
import os

p = 'modules/reports/pdf/results_table.py'
s = open(p, encoding='utf-8').read()

# Current header row
old = "        Paragraph('Result', header_style),"
new = "        Paragraph(order.created_at.strftime('%d-%b-%y') if order.created_at else 'Result', header_style),"

if 'strftime(\'%d-%b-%y\') if order.created_at' not in s:
    s = s.replace(old, new, 1)
    open(p, 'w', encoding='utf-8').write(s)
    print('OK  - Result header renamed to current date')
else:
    print('SKIP - already renamed')

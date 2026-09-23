# Remove placeholder and icon from Mobile No. field
p = 'modules/orders/templates/orders/new.html'
s = open(p, encoding='utf-8').read()

import re

# Remove the telephone icon
s = re.sub(
    r'\s*<i class="bi bi-telephone lookup-icon"></i>',
    '',
    s,
    count=1,
)

# Remove placeholder="0300-1234567"
s = s.replace('placeholder="0300-1234567"\n                       ', '')
s = s.replace('placeholder="0300-1234567" ', '')
s = s.replace('placeholder="0300-1234567"', '')

open(p, 'w', encoding='utf-8').write(s)
print('OK  - icon + placeholder removed from Mobile No. field')

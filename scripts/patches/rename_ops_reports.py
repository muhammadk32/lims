# Rename "Reports" in Operations dropdown to "Test Reports"
p = 'templates/layout/topnav.html'
s = open(p, encoding='utf-8').read()

# Only change the one inside the Operations dropdown (it has bi-file-earmark-medical icon)
old = '<i class="bi bi-file-earmark-medical"></i> Reports'
new = '<i class="bi bi-file-earmark-medical"></i> Test Reports'

if new in s:
    print('SKIP - already renamed')
elif old in s:
    s = s.replace(old, new, 1)
    open(p, 'w', encoding='utf-8').write(s)
    print('OK  - Operations > Reports renamed to "Test Reports"')
else:
    print('WARN - anchor not found')

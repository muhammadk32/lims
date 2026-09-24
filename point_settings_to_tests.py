# Point topnav Lab Test Settings link to /tests/
p = 'templates/layout/topnav.html'
s = open(p, encoding='utf-8').read()

old = "{{ url_for('test_settings.formats') }}"
new = "{{ url_for('tests.list_tests') }}"

if 'test_settings.formats' in s:
    # Only replace the top-level one (last occurrence near </nav>)
    # Safer: replace the one inside the top-level block (which is the only one in the file now)
    s = s.replace(old, new)
    open(p, 'w', encoding='utf-8').write(s)
    print('OK  - topnav link points to /tests/')
elif 'tests.list_tests' in s:
    print('SKIP - already points to /tests/')
else:
    print('WARN - anchor not found')

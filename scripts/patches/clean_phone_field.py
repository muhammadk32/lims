# Make Mobile No. field plain — no placeholder, no icon
p = 'modules/orders/templates/orders/new.html'
s = open(p, encoding='utf-8').read()

# Remove the lookup-icon wrapper
old_block = '''              <div class="mobile-lookup-wrap">
                <i class="bi bi-telephone lookup-icon"></i>
                <input type="tel" class="form-control" id="lookupPhone"
                       name="phone"
                       placeholder="0300-1234567"
                       {% if 'patient_phone' in config.required_fields %}required{% endif %}>
                <div class="lookup-results" id="lookupResults" style="display: none;"></div>
              </div>'''

new_block = '''              <div class="mobile-lookup-wrap">
                <input type="tel" class="form-control" id="lookupPhone"
                       name="phone"
                       {% if 'patient_phone' in config.required_fields %}required{% endif %}>
                <div class="lookup-results" id="lookupResults" style="display: none;"></div>
              </div>'''

if old_block in s:
    s = s.replace(old_block, new_block, 1)
    open(p, 'w', encoding='utf-8').write(s)
    print('OK  - placeholder + icon removed')
else:
    # Try a looser match
    import re
    s = re.sub(
        r'<i class="bi bi-telephone lookup-icon"></i>\s*\n\s*',
        '',
        s,
        count=1,
    )
    s = s.replace('placeholder="0300-1234567"\n                       ', '')
    s = s.replace('placeholder="0300-1234567" ', '')
    open(p, 'w', encoding='utf-8').write(s)
    print('OK  - placeholder + icon removed (loose match)')

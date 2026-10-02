"""
Revisit: skip the pill, show pre-filled editable form immediately.
"""
p = 'static/js/reception.js'
s = open(p, encoding='utf-8').read()

if 'REVISIT_DIRECT_FORM' in s:
    print('SKIP - already patched')
else:
    # Find the prefill function and change the pill logic
    old = '''    var selectedBox = document.getElementById('selectedPatientBox');
    var nameSpan = document.getElementById('spName');
    var metaSpan = document.getElementById('spMeta');
    var badge = document.getElementById('patientBadge');
    var newForm = document.getElementById('newPatientForm');
    var lookupPhone = document.getElementById('lookupPhone');

    if (selectedBox && nameSpan && metaSpan) {
      nameSpan.textContent = p.name;
      metaSpan.textContent = p.code
        + (p.age ? ' \\u00b7 ' + p.age + 'y' : '')
        + (p.gender ? ' \\u00b7 ' + p.gender : '');
      selectedBox.style.display = 'block';
      if (newForm) newForm.style.display = 'none';
      if (badge) {
        badge.textContent = 'Existing';
        badge.className = 'badge bg-success';
      }
      if (lookupPhone) {
        lookupPhone.value = p.phone || '';
        lookupPhone.disabled = true;
      }
    }'''

    new = '''    // ===== REVISIT_DIRECT_FORM =====
    // Skip the pill entirely. Show the form pre-filled and editable.
    var badge = document.getElementById('patientBadge');
    if (badge) {
      badge.textContent = 'Existing';
      badge.className = 'badge bg-success';
    }

    // Fill fields (already done above via setField calls).
    // Phone field: keep it filled but disabled so typeahead doesn't fight.
    // Actually leave it enabled — allow editing.
    var lookupPhone = document.getElementById('lookupPhone');
    if (lookupPhone) {
      lookupPhone.value = p.phone || '';
      lookupPhone.disabled = false;
    }

    // Make sure newPatientForm is visible (form is default)
    var newForm = document.getElementById('newPatientForm');
    if (newForm) newForm.style.display = '';

    // Hide the pill (in case any prior code showed it)
    var selectedBox = document.getElementById('selectedPatientBox');
    if (selectedBox) selectedBox.style.display = 'none';'''

    if old in s:
        s = s.replace(old, new, 1)
        open(p, 'w', encoding='utf-8').write(s)
        print('OK  - pill skipped; form pre-filled directly')
    else:
        print('WARN - pill block not found')
        # Try to find it
        idx = s.find('selectedBox.style.display')
        if idx != -1:
            print(repr(s[max(0,idx-400):idx+400]))

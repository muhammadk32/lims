# Feature 2 (restart from where it crashed) — skip the already-done steps

# ============================================================
# 2b. Prefill patient_id hidden input (unconditional now)
# ============================================================
tp = 'modules/orders/templates/orders/new.html'
t = open(tp, encoding='utf-8').read()

old_pid = '<input type="hidden" name="patient_id" id="patientIdInput" value="">'
new_pid = '<input type="hidden" name="patient_id" id="patientIdInput" value="{{ prefill_patient.id if prefill_patient else \'\' }}">'

if old_pid in t and 'prefill_patient.id' not in t:
    t = t.replace(old_pid, new_pid, 1)
    print('OK  - template: patient_id pre-filled')
elif 'prefill_patient.id' in t:
    print('SKIP - patient_id already pre-filled')
else:
    print('WARN - patient_id anchor not found')

# ============================================================
# 2c. Add __REVISIT_DATA script
# ============================================================
if 'window.__REVISIT_DATA' not in t:
    marker = '{% block scripts %}'
    data_script = '''<script>
  window.__REVISIT_DATA = {
    patient: {% if prefill_patient %}{
      id: {{ prefill_patient.id }},
      code: {{ prefill_patient.patient_code|tojson }},
      name: {{ prefill_patient.full_name|tojson }},
      age: {{ prefill_patient.age or 0 }},
      gender: {{ (prefill_patient.gender or '')|tojson }},
      phone: {{ (prefill_patient.phone or '')|tojson }},
      email: {{ (prefill_patient.email or '')|tojson }},
      address: {{ (prefill_patient.address or '')|tojson }},
      blood_group: {{ (prefill_patient.blood_group or '')|tojson }}
    }{% else %}null{% endif %},
    tests: {{ prefill_tests|tojson }}
  };
</script>

'''
    if marker in t:
        t = t.replace(marker, data_script + marker, 1)
        print('OK  - template: __REVISIT_DATA script added')
    else:
        print('WARN - scripts block marker not found')

open(tp, 'w', encoding='utf-8').write(t)


# ============================================================
# 3. CSS
# ============================================================
import os
cp = 'static/css/reception.css'
c = open(cp, encoding='utf-8').read()

if '.revisit-banner' not in c:
    css = '''

/* ============================================================
   Revisit Banner
   ============================================================ */
.revisit-banner {
  border: 1px solid #0d6efd;
  background: #e7f1ff;
  color: #084298;
  padding: 8px 12px;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.82rem;
}
.revisit-banner i { color: #0d6efd; font-size: 1rem; }
.revisit-banner strong {
  text-transform: uppercase;
  letter-spacing: 0.04em;
  font-size: 0.72rem;
}
.revisit-info {
  font-family: Consolas, Monaco, monospace;
  font-size: 0.78rem;
  color: #495057;
}
.revisit-close {
  margin-left: auto;
  background: transparent;
  border: none;
  color: #084298;
  cursor: pointer;
  padding: 2px 6px;
  font-size: 0.9rem;
}
.revisit-close:hover { background: rgba(13, 110, 253, 0.15); }
'''
    open(cp, 'w', encoding='utf-8').write(c + css)
    print('OK  - reception.css: revisit banner styles')
else:
    print('SKIP - revisit banner styles already present')


# ============================================================
# 4. JS
# ============================================================
jp = 'static/js/reception.js'
j = open(jp, encoding='utf-8').read()

if 'REVISIT_PREFILL' not in j:
    anchor = "  /* ======================== INIT ======================== */"
    block = '''  /* ======================== REVISIT_PREFILL ======================== */
  (function prefillFromRevisit() {
    var data = window.__REVISIT_DATA;
    if (!data || !data.patient) return;

    var p = data.patient;

    var pidInput = document.getElementById('patientIdInput');
    if (pidInput) pidInput.value = p.id;

    function setField(name, value) {
      if (value === undefined || value === null || value === '') return;
      var el = document.querySelector('[name="' + name + '"]');
      if (!el) el = document.getElementById('fld_' + name);
      if (!el) return;
      if (el.type === 'checkbox') el.checked = !!value;
      else el.value = value;
    }

    setField('phone', p.phone);
    setField('patient_name', p.name);
    setField('gender', p.gender);
    setField('patient_email', p.email);
    setField('email', p.email);
    setField('patient_address', p.address);
    setField('address', p.address);
    setField('blood_group', p.blood_group);

    var ageVal = document.getElementById('ageValue');
    var ageUnit = document.getElementById('ageUnit');
    var ageHidden = document.getElementById('fld_patient_age');
    if (ageVal && p.age) {
      ageVal.value = p.age;
      if (ageUnit) ageUnit.value = 'years';
      if (ageHidden) ageHidden.value = p.age;
    }

    var selectedBox = document.getElementById('selectedPatientBox');
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
    }

    if (data.tests && data.tests.length && typeof addTest === 'function') {
      data.tests.forEach(function (t) {
        var already = state.selectedTests.some(function (x) { return x.id === t.id; });
        if (already) return;
        addTest({
          id: t.id,
          code: t.code,
          name: t.name,
          price: t.price,
          is_panel: t.is_panel,
          parameter_count: t.parameter_count || 0,
        });
      });
    }
  })();

'''
    if anchor in j:
        j = j.replace(anchor, block + anchor, 1)
        open(jp, 'w', encoding='utf-8').write(j)
        print('OK  - reception.js: revisit prefill logic added')
    else:
        print('WARN - INIT anchor not found')
else:
    print('SKIP - revisit prefill already present')

print()
print('=' * 55)
print('Done. Restart Flask and test.')
print('=' * 55)

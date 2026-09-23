"""
Feature 2: Revisit prefill
- /orders/new?patient_id=X&revisit_from=Y
- Auto-fills patient fields + pre-selects tests
- Green "Revisiting from Lab #XXXX" banner
- Patient fields editable
- Archived tests skipped silently
"""
import os

# ============================================================
# 1. Route — read query params and pass to template
# ============================================================
rp = 'modules/orders/routes.py'
r = open(rp, encoding='utf-8').read()

old = """def new_order():
    from modules.billing.models import PaymentMethod
    from modules.form_settings.helpers import get_form_config

    if request.method == 'POST':
        return _handle_new_order_post()

    return render_template(
        'orders/new.html',
        config=get_form_config(),
        doctors=q.get_doctors(),
        payment_methods=PaymentMethod.CHOICES,
        payment_method_labels=PaymentMethod.LABELS,
        now=datetime.now(),
    )"""

new = """def new_order():
    from modules.billing.models import PaymentMethod
    from modules.form_settings.helpers import get_form_config
    from modules.patients.models import Patient
    from modules.orders.models import Order

    if request.method == 'POST':
        return _handle_new_order_post()

    # ---------- Revisit prefill ----------
    prefill_patient = None
    prefill_tests = []
    revisit_order = None
    skipped_count = 0

    pid = request.args.get('patient_id', type=int)
    revisit_from = request.args.get('revisit_from', type=int)

    if pid:
        prefill_patient = Patient.query.get(pid)

    if revisit_from:
        revisit_order = Order.query.get(revisit_from)
        if revisit_order and prefill_patient is None:
            prefill_patient = revisit_order.patient

        if revisit_order:
            for item in revisit_order.top_level_items:
                t = item.test
                if not t or not t.is_active:
                    skipped_count += 1
                    continue
                prefill_tests.append({
                    'id': t.id,
                    'code': t.code,
                    'name': t.name,
                    'price': t.price or 0,
                    'is_panel': bool(t.is_panel),
                    'parameter_count': len(t.get_parameters()) if t.is_panel else 0,
                })

    return render_template(
        'orders/new.html',
        config=get_form_config(),
        doctors=q.get_doctors(),
        payment_methods=PaymentMethod.CHOICES,
        payment_method_labels=PaymentMethod.LABELS,
        now=datetime.now(),
        prefill_patient=prefill_patient,
        prefill_tests=prefill_tests,
        revisit_order=revisit_order,
        skipped_count=skipped_count,
    )"""

if old in r:
    r = r.replace(old, new, 1)
    open(rp, 'w', encoding='utf-8').write(r)
    print('OK  - routes.py: revisit prefill logic added')
else:
    print('WARN - new_order anchor not found')


# ============================================================
# 2. Template — add banner + prefill data-script
# ============================================================
tp = 'modules/orders/templates/orders/new.html'
t = open(tp, encoding='utf-8').read()

# 2a. Insert revisit banner at top of rec-page
old_top = '''<div class="rec-page" id="recPage" data-currency="{{ config.currency_symbol }}">

  <div class="rec-header">'''

new_top = '''<div class="rec-page" id="recPage" data-currency="{{ config.currency_symbol }}">

  {% if revisit_order and prefill_patient %}
  <div class="revisit-banner" id="revisitBanner">
    <i class="bi bi-arrow-repeat"></i>
    <strong>REVISITING from Lab #{{ revisit_order.order_code }}</strong>
    <span class="revisit-info">
      {{ prefill_patient.full_name }} ({{ prefill_patient.patient_code }})
      · {{ prefill_tests|length }} test{{ 's' if prefill_tests|length != 1 }} pre-filled
      {% if skipped_count %} · {{ skipped_count }} archived skipped{% endif %}
    </span>
    <button type="button" class="revisit-close" onclick="document.getElementById('revisitBanner').remove();">
      <i class="bi bi-x-lg"></i>
    </button>
  </div>
  {% endif %}

  <div class="rec-header">'''

if 'revisit-banner' not in t and old_top in t:
    t = t.replace(old_top, new_top, 1)
    print('OK  - template: revisit banner added')

# 2b. Prefill patient_id hidden input
if prefill_patient is not None:
    old_pid = '<input type="hidden" name="patient_id" id="patientIdInput" value="">'
    new_pid = '<input type="hidden" name="patient_id" id="patientIdInput" value="{{ prefill_patient.id if prefill_patient else "" }}">'
    if old_pid in t:
        t = t.replace(old_pid, new_pid, 1)
        print('OK  - template: patient_id pre-filled')

# 2c. Add a data script at the end before {% endblock %} of content
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

open(tp, 'w', encoding='utf-8').write(t)


# ============================================================
# 3. CSS — revisit banner
# ============================================================
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
# 4. JS — prefill patient fields + pre-select tests
# ============================================================
jp = 'static/js/reception.js'
j = open(jp, encoding='utf-8').read()

if 'REVISIT_PREFILL' not in j:
    # Insert after the closing of the IIFE — actually inside, before "/* ====== INIT ====== */"
    anchor = "  /* ======================== INIT ======================== */"
    block = '''  /* ======================== REVISIT_PREFILL ======================== */
  (function prefillFromRevisit() {
    var data = window.__REVISIT_DATA;
    if (!data || !data.patient) return;

    var p = data.patient;

    // --- Patient fields ---
    // Set the hidden patient_id input (already set server-side, this is a safety net)
    var pidInput = document.getElementById('patientIdInput');
    if (pidInput) pidInput.value = p.id;

    // Fill visible fields by name attribute
    function setField(name, value) {
      if (value === undefined || value === null || value === '') return;
      var el = document.querySelector('[name="' + name + '"]');
      if (!el) {
        // fall back to id pattern fld_<name>
        el = document.getElementById('fld_' + name);
      }
      if (!el) return;
      if (el.type === 'checkbox') {
        el.checked = !!value;
      } else {
        el.value = value;
      }
    }

    setField('phone', p.phone);
    setField('patient_name', p.name);
    setField('gender', p.gender);
    setField('patient_email', p.email);
    setField('email', p.email);
    setField('patient_address', p.address);
    setField('address', p.address);
    setField('blood_group', p.blood_group);

    // Age: number + unit
    var ageVal = document.getElementById('ageValue');
    var ageUnit = document.getElementById('ageUnit');
    var ageHidden = document.getElementById('fld_patient_age');
    if (ageVal && p.age) {
      ageVal.value = p.age;
      if (ageUnit) ageUnit.value = 'years';
      if (ageHidden) ageHidden.value = p.age;
    }

    // Show the "existing patient" pill
    var selectedBox = document.getElementById('selectedPatientBox');
    var nameSpan = document.getElementById('spName');
    var metaSpan = document.getElementById('spMeta');
    var badge = document.getElementById('patientBadge');
    var newForm = document.getElementById('newPatientForm');
    var lookupPhone = document.getElementById('lookupPhone');

    if (selectedBox && nameSpan && metaSpan) {
      nameSpan.textContent = p.name;
      metaSpan.textContent = p.code
        + (p.age ? ' · ' + p.age + 'y' : '')
        + (p.gender ? ' · ' + p.gender : '');
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

      // Make patient fields read-write (not disabled) so reception can edit
      // (the standard selectPatient would disable them — we skip that)
    }

    // --- Pre-select tests ---
    if (data.tests && data.tests.length) {
      data.tests.forEach(function (t) {
        var already = state.selectedTests.some(function (x) { return x.id === t.id; });
        if (already) return;
        if (typeof addTest === 'function') {
          addTest({
            id: t.id,
            code: t.code,
            name: t.name,
            price: t.price,
            is_panel: t.is_panel,
            parameter_count: t.parameter_count || 0,
          });
        }
      });
    }
  })();

'''
    if anchor in j:
        j = j.replace(anchor, block + anchor, 1)
        open(jp, 'w', encoding='utf-8').write(j)
        print('OK  - reception.js: revisit prefill logic added')
    else:
        print('WARN - INIT anchor not found in reception.js')
else:
    print('SKIP - revisit prefill already present')


print()
print('=' * 55)
print('Done. Restart Flask and:')
print('  1. Open /patients/history?q=<phone>')
print('  2. Expand a patient card')
print('  3. Click Revisit on a row')
print('  4. Registration form opens with patient + tests pre-filled')
print('=' * 55)

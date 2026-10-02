"""Fix: move __REVISIT_DATA script inside block content, before endblock."""
p = 'modules/orders/templates/orders/new.html'

with open(p, encoding='utf-8') as f:
    content = f.read()

# Find the __REVISIT_DATA script block (if it exists)
start = content.find('<script>\n  window.__REVISIT_DATA')
if start == -1:
    start = content.find('<script>window.__REVISIT_DATA')
if start == -1:
    start = content.find('window.__REVISIT_DATA')
    if start != -1:
        # Find the enclosing <script>...</script>
        s_before = content.rfind('<script>', 0, start)
        if s_before != -1:
            start = s_before
        s_after = content.find('</script>', start)
        end = s_after + len('</script>') if s_after != -1 else -1
else:
    s_after = content.find('</script>', start)
    end = s_after + len('</script>') if s_after != -1 else -1

if start == -1 or end == -1:
    print('SKIP - no __REVISIT_DATA script found in template')
    # Let's insert it fresh
    marker = '{% block scripts %}'
    if marker in content:
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
        content = content.replace(marker, data_script + marker, 1)
        with open(p, 'w', encoding='utf-8') as f:
            f.write(content)
        print('OK  - __REVISIT_DATA script inserted fresh')
else:
    # Extract the script block and move it INSIDE content block
    script_block = content[start:end]

    # Remove it from its current location
    content = content[:start] + content[end:]

    # Find the LAST {% endblock %} that closes block content (before block scripts)
    scripts_marker = '{% block scripts %}'
    scripts_idx = content.find(scripts_marker)

    if scripts_idx == -1:
        print('ERR - block scripts not found')
    else:
        # Insert the script right before block scripts
        content = content[:scripts_idx] + script_block + '\n\n' + content[scripts_idx:]
        with open(p, 'w', encoding='utf-8') as f:
            f.write(content)
        print('OK  - __REVISIT_DATA moved before block scripts')

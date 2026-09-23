"""
Patient History — make cards collapsible
"""
import os

p = 'modules/patients/templates/patients/history.html'
s = open(p, encoding='utf-8').read()

# 1. Update the card header to be clickable with a chevron
old_header = '''      <div class="ph-card-header">
        <div>
          <span class="pname">{{ p.full_name }}</span>
          <span class="pmeta">
            · {{ p.patient_code }}
            · {{ p.phone or 'no phone' }}
            {% if p.compute_age() %} · {{ p.compute_age() }}y{% endif %}
            {% if p.gender %} · {{ p.gender }}{% endif %}
          </span>
        </div>
        <span class="pcount">
          {{ patient_visits|length }} visit{{ 's' if patient_visits|length != 1 }}
        </span>
      </div>'''

new_header = '''      <div class="ph-card-header" onclick="togglePatient({{ p.id }})"
           style="cursor: pointer; user-select: none;">
        <div>
          <i class="bi bi-chevron-right ph-chevron" id="chev-{{ p.id }}"
             style="transition: transform 0.15s; display: inline-block; width: 14px;"></i>
          <span class="pname">{{ p.full_name }}</span>
          <span class="pmeta">
            · {{ p.patient_code }}
            · {{ p.phone or 'no phone' }}
            {% if p.compute_age() %} · {{ p.compute_age() }}y{% endif %}
            {% if p.gender %} · {{ p.gender }}{% endif %}
          </span>
        </div>
        <span class="pcount">
          {{ patient_visits|length }} visit{{ 's' if patient_visits|length != 1 }}
        </span>
      </div>'''

if old_header in s:
    s = s.replace(old_header, new_header, 1)
    print('OK  - header made clickable')
else:
    print('WARN - header block not found')

# 2. Wrap the table in a collapsible div
old_table_open = '''      {% if patient_visits %}
      <table class="ph-table">'''
new_table_open = '''      <div class="ph-visits" id="visits-{{ p.id }}" style="display: none;">
      {% if patient_visits %}
      <table class="ph-table">'''
if old_table_open in s:
    s = s.replace(old_table_open, new_table_open, 1)
    print('OK  - table wrapped in collapsible div')

# 3. Close the collapsible div after the table
old_table_close = '''      </table>
      {% else %}
      <div style="padding: 14px; text-align: center; color: #6c757d; font-style: italic;">
        No visits recorded yet.
      </div>
      {% endif %}'''
new_table_close = '''      </table>
      {% else %}
      <div style="padding: 14px; text-align: center; color: #6c757d; font-style: italic;">
        No visits recorded yet.
      </div>
      {% endif %}
      </div>'''
if old_table_close in s:
    s = s.replace(old_table_close, new_table_close, 1)
    print('OK  - collapsible div closed')

# 4. Add JS at the end
if 'togglePatient' not in s or 'function togglePatient' not in s:
    js_block = '''

{% block scripts %}
<script>
function togglePatient(pid) {
  var visits = document.getElementById('visits-' + pid);
  var chev = document.getElementById('chev-' + pid);
  if (!visits) return;
  var open = visits.style.display !== 'none';
  visits.style.display = open ? 'none' : 'block';
  if (chev) chev.style.transform = open ? 'rotate(0deg)' : 'rotate(90deg)';
}

// Auto-expand if only one patient in results
document.addEventListener('DOMContentLoaded', function () {
  var cards = document.querySelectorAll('.ph-visits');
  if (cards.length === 1) {
    var id = cards[0].id.replace('visits-', '');
    togglePatient(id);
  }
});
</script>
{% endblock %}
'''
    # Insert before final {% endblock %}
    end = s.rfind('{% endblock %}')
    if end != -1:
        s = s[:end] + js_block + '\n' + s[end:]
        print('OK  - JS toggle added')

open(p, 'w', encoding='utf-8').write(s)
print()
print('Done. Restart Flask to see collapsible cards.')

"""
Hide negative per-row values from display.
Keep true (possibly negative) stored amount.
Total nets everything — as before.
"""
import os

# ---------- 1. Revert create_order to store true value (no floor) ----------
sp = 'modules/orders/services.py'
s = open(sp, encoding='utf-8').read()

# Ensure no floor in create_order
old = """                _amt = (_sub * (_pct / 100.0)) - _disc
                order.commission_amount = round(_amt, 2)"""
new = """                _amt = (_sub * (_pct / 100.0)) - _disc
                order.commission_amount = round(_amt, 2)  # may be negative; UI hides sign"""
if old in s:
    s = s.replace(old, new, 1)
    open(sp, 'w', encoding='utf-8').write(s)
    print('OK  - create_order stores true value')
elif 'UI hides sign' in s:
    print('SKIP - create_order already fine')


# ---------- 2. Detail template: hide negative per-row, footnote for total ----------
tp = 'modules/analytics/templates/analytics/commission_detail.html'
t = open(tp, encoding='utf-8').read()

# --- 2a. Per-row share cell ---
old_row = '<td class="num fw-semibold" style="{% if r.commission < 0 %}color: #dc3545;{% endif %}">{{ r.commission | money }}</td>'
new_row = '''<td class="num fw-semibold">
        {% if r.commission < 0 %}
          <span class="muted" title="Adjusted against other entries">0.00</span>
        {% else %}
          {{ r.commission | money }}
        {% endif %}
      </td>'''

if old_row in t:
    t = t.replace(old_row, new_row, 1)
    print('OK  - detail: negative rows show 0.00')
elif 'Adjusted against other entries' in t:
    print('SKIP - detail already hides negatives')
else:
    # Try alternate cell pattern
    alt = '<td class="num fw-semibold">{{ r.commission | money }}</td>'
    if alt in t:
        t = t.replace(alt, new_row, 1)
        print('OK  - detail: negative rows show 0.00 (alt pattern)')
    else:
        print('WARN - row commission cell not found')


# --- 2b. Add a small note under the table ---
if 'Adjusted against over-discounted orders' not in t:
    anchor = '{% endblock %}'
    note = '''

<div style="margin-top: 10px; font-size: 0.72rem; color: #6c757d; font-style: italic;">
  <i class="bi bi-info-circle"></i>
  Total is calculated after netting adjustments from over-discounted orders.
  Individual rows show the payable amount only.
</div>
'''
    # Insert before the LAST {% endblock %}
    idx = t.rfind(anchor)
    if idx != -1:
        t = t[:idx] + note + t[idx:]
        print('OK  - note added below total')


open(tp, 'w', encoding='utf-8').write(t)


# ---------- 3. Summary page — total already nets correctly, no change ----------
print('OK  - summary page: no change (total already nets)')

print()
print('=' * 55)
print('Done. Reload /analytics/commissions/<doctor>')
print('Row 0926-23 will show 0.00; total stays correct.')
print('=' * 55)

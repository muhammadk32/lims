import os
TPL = 'templates/test_settings'

UNITS = """{# ============ UNITS TAB (stub) ============ #}
<div class="ts-stub">
  <i class="bi bi-rulers ts-stub-icon"></i>
  <div class="ts-stub-title">Units &amp; Reference Ranges</div>
  <div class="ts-stub-text">Manage units (mg/dL, mmol/L, ...) and age/gender-specific reference ranges.</div>
  <div class="ts-stub-badge">
    <i class="bi bi-hourglass-split"></i> Coming in a future update
  </div>
</div>
"""

BULK = """{# ============ BULK TAB (stub) ============ #}
<div class="ts-stub">
  <i class="bi bi-upload ts-stub-icon"></i>
  <div class="ts-stub-title">Bulk Actions</div>
  <div class="ts-stub-text">Import from Excel/CSV, export the catalog, run cleanup tools.</div>
  <div class="ts-stub-badge">
    <i class="bi bi-hourglass-split"></i> Coming in a future update
  </div>
</div>
"""

with open(os.path.join(TPL, '_units.html'), 'w', encoding='utf-8') as f:
    f.write(UNITS)
print('OK  - _units.html created')

with open(os.path.join(TPL, '_bulk.html'), 'w', encoding='utf-8') as f:
    f.write(BULK)
print('OK  - _bulk.html created')

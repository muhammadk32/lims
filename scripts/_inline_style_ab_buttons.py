"""Inline-style the action buttons — cannot be overridden."""
import io, os, re
path = os.path.join("templates", "settings", "antibiotics.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

# Force width via inline style on each button in ab-actions
src = re.sub(
    r'<button type="button" class="ab-btn ab-btn-sm ab-btn-edit"',
    '<button type="button" class="ab-btn ab-btn-sm ab-btn-edit" style="min-width:64px!important;height:32px!important;padding:0 14px!important;font-size:12px!important;display:inline-flex!important;align-items:center!important;justify-content:center!important;gap:5px!important;"',
    src
)
src = re.sub(
    r'<button class="ab-btn ab-btn-sm \{\{ .ab-btn-warn. if a\.is_active else .ab-btn-ok. \}\}"',
    '<button class="ab-btn ab-btn-sm {{ \'ab-btn-warn\' if a.is_active else \'ab-btn-ok\' }}" style="min-width:120px!important;height:32px!important;padding:0 14px!important;font-size:12px!important;display:inline-flex!important;align-items:center!important;justify-content:center!important;font-weight:700!important;text-transform:uppercase!important;letter-spacing:0.03em!important;"',
    src
)
src = re.sub(
    r'<button class="ab-btn ab-btn-sm ab-btn-danger"',
    '<button class="ab-btn ab-btn-sm ab-btn-danger" style="width:32px!important;min-width:32px!important;height:32px!important;padding:0!important;display:inline-flex!important;align-items:center!important;justify-content:center!important;font-size:13px!important;"',
    src
)

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("inline styles applied to all 3 buttons")

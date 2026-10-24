"""Include admin_theme.css on reports/analytics/billing pages."""
import io, os
path = os.path.join("templates", "base.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

old = "{% if request.path.startswith('/settings/') or request.path.startswith('/users/') or request.path.startswith('/audit/') or request.path.startswith('/patients/') %}"
new = "{% if request.path.startswith('/settings/') or request.path.startswith('/users/') or request.path.startswith('/audit/') or request.path.startswith('/patients/') or request.path.startswith('/billing/') or request.path.startswith('/analytics/') or request.path.startswith('/reports/') %}"

if old in src:
    src = src.replace(old, new, 1)
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("conditional extended")
else:
    print("anchor MISS")

"""Include admin_theme.css in base.html conditionally on path."""
import io, os
path = os.path.join("templates", "base.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

if "admin_theme.css" not in src:
    include = (
"{% if request.path.startswith('/settings/') or request.path.startswith('/users/') or request.path.startswith('/audit/') or request.path.startswith('/patients/') %}" + nl +
'  <link rel="stylesheet" href="{{ url_for(\'static\', filename=\'css/admin_theme.css\') }}">' + nl +
"{% endif %}"
    )
    # find last CSS link to insert after
    import re
    matches = list(re.finditer(r'<link[^>]+href="[^"]+\.css[^"]*"[^>]*>', src))
    if matches:
        last = matches[-1]
        src = src[:last.end()] + nl + include + src[last.end():]
        print("admin_theme.css injected conditionally")
    else:
        print("no CSS links found — insert manually")
else:
    print("already present")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

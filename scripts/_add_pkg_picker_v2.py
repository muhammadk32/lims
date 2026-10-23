"""Insert package dropdown using exact whitespace anchor."""
import io, os
path = os.path.join("modules", "orders", "templates", "orders", "new.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

anchor = "          {% if tests_section and tests_section.is_visible %}" + nl
pkg_block = (
"          {% if tests_section and tests_section.is_visible %}" + nl +
nl +
"          {# ===== Health Package quick-pick ===== #}" + nl +
"          <div style=\"background:#f0f4ff; border:2px solid #212529; border-radius:8px; padding:8px 12px; margin-bottom:8px; display:flex; align-items:center; gap:10px;\">" + nl +
"            <label style=\"font-weight:700; font-size:0.78rem; text-transform:uppercase; color:#495057; margin:0; white-space:nowrap;\">" + nl +
"              <i class=\"bi bi-box-seam\"></i> Health Package" + nl +
"            </label>" + nl +
"            <select id=\"packagePicker\" class=\"form-select form-select-sm\" style=\"max-width:340px;\" onchange=\"if(typeof window.__onPackagePick==='function'){window.__onPackagePick(this.value);}\">" + nl +
"              <option value=\"\">— Select a package —</option>" + nl +
"              {% for pkg in (packages or []) %}" + nl +
"              <option value=\"{{ pkg.id }}\" data-price=\"{{ pkg.price or 0 }}\" data-code=\"{{ pkg.code }}\" data-name=\"{{ pkg.name }}\" data-is-panel=\"{{ 1 if pkg.is_panel else 0 }}\">{{ pkg.name }} ({{ pkg.code }})</option>" + nl +
"              {% endfor %}" + nl +
"            </select>" + nl +
"            <small class=\"text-muted\" style=\"font-size:0.72rem;\">Adds package to basket</small>" + nl +
"          </div>" + nl
)

if "id=\"packagePicker\"" not in src:
    if anchor in src:
        src = src.replace(anchor, pkg_block, 1)
        print("dropdown inserted")
    else:
        print("ANCHOR MISS again")
else:
    print("already present")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

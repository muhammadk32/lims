"""Move package picker to top-right, restyle."""
import io, os
path = os.path.join("modules", "orders", "templates", "orders", "new.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

# 1) remove the current package block (from comment marker to its closing </div>)
old_start = src.find("          {# ===== Health Package quick-pick ===== #}")
if old_start < 0:
    print("old block not found")
else:
    # find the </div> that closes the pkg block (last </div> before the search input-group)
    next_anchor = src.find("          <div class=\"input-group input-group-sm mb-2\">", old_start)
    if next_anchor > 0:
        # everything from old_start to next_anchor is the block to remove
        src = src[:old_start] + src[next_anchor:]
        print("old package block removed")
    else:
        print("search input anchor not found after block")

# 2) insert new package bar ABOVE the "Tests & Panels" section title
# Find the section title div
title_anchor = "        <div class=\"rec-cell-title\">" + nl + "          <i class=\"bi bi-clipboard2-pulse\"></i> Tests &amp; Panels"

pkg_bar = (
"        <div style=\"display:flex; justify-content:flex-end; margin-bottom:6px;\">" + nl +
"          <div style=\"background:linear-gradient(135deg,#1a3d7c 0%,#0d6efd 100%); color:#fff; border-radius:10px; padding:8px 14px; display:flex; align-items:center; gap:10px; box-shadow:0 2px 6px rgba(0,0,0,0.2);\">" + nl +
"            <label style=\"font-weight:700; font-size:0.78rem; text-transform:uppercase; color:#ffd166; margin:0; white-space:nowrap; letter-spacing:0.04em;\">" + nl +
"              <i class=\"bi bi-box-seam-fill\"></i> Health Package" + nl +
"            </label>" + nl +
"            <select id=\"packagePicker\" class=\"form-select form-select-sm\" style=\"max-width:300px; background:#fff; color:#1a3d7c; font-weight:600; border:none;\" onchange=\"if(typeof window.__onPackagePick==='function'){window.__onPackagePick(this.value);}\">" + nl +
"              <option value=\"\">— Select a package —</option>" + nl +
"              {% for pkg in (packages or []) %}" + nl +
"              <option value=\"{{ pkg.id }}\" data-price=\"{{ pkg.price or 0 }}\" data-code=\"{{ pkg.code }}\" data-name=\"{{ pkg.name }}\" data-is-panel=\"{{ 1 if pkg.is_panel else 0 }}\">{{ pkg.name }} ({{ pkg.code }})</option>" + nl +
"              {% endfor %}" + nl +
"            </select>" + nl +
"          </div>" + nl +
"        </div>" + nl
)

if title_anchor in src:
    src = src.replace(title_anchor, pkg_bar + title_anchor, 1)
    print("new package bar inserted above title")
else:
    print("title anchor MISS")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

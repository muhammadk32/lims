"""Insert package dropdown above test search box."""
import io, os
path = os.path.join("modules", "orders", "templates", "orders", "new.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

anchor = (
"          <div class=\"input-group input-group-sm mb-2\">" + nl +
"            <span class=\"input-group-text\"><i class=\"bi bi-search\"></i></span>"
)

pkg_dropdown = (
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
"          </div>" + nl +
nl +
anchor
)

if "id=\"packagePicker\"" not in src:
    if anchor in src:
        src = src.replace(anchor, pkg_dropdown, 1)
        print("package dropdown inserted")
    else:
        print("ANCHOR MISS")
else:
    print("already present")

# add JS handler — insert before {% endblock %} of scripts
if "window.__onPackagePick" not in src or "onPackagePickImpl" not in src:
    js = (
nl + "<script>" + nl +
"window.__onPackagePick = function(pkgId) {" + nl +
"  if (!pkgId) return;" + nl +
"  var sel = document.getElementById('packagePicker');" + nl +
"  var opt = sel.options[sel.selectedIndex];" + nl +
"  if (!opt) return;" + nl +
"  var t = {" + nl +
"    id: parseInt(pkgId)," + nl +
"    code: opt.dataset.code," + nl +
"    name: opt.dataset.name," + nl +
"    price: parseFloat(opt.dataset.price) || 0," + nl +
"    is_panel: opt.dataset.isPanel === '1'," + nl +
"    parameter_count: 0," + nl +
"    sample_type: ''," + nl +
"    turnaround_hours: 24" + nl +
"  };" + nl +
"  if (typeof addTest === 'function') {" + nl +
"    addTest(t);" + nl +
"  } else if (window.state && typeof window.state.selectedTests !== 'undefined') {" + nl +
"    window.state.selectedTests.push(t);" + nl +
"    if (typeof renderSelectedTests === 'function') renderSelectedTests();" + nl +
"    if (typeof updateBilling === 'function') updateBilling();" + nl +
"  } else {" + nl +
"    console.warn('addTest not found — cannot add package');" + nl +
"  }" + nl +
"  sel.selectedIndex = 0;" + nl +
"};" + nl +
"</script>" + nl
    )
    # Insert before closing {% endblock %} at end of file
    last_endblock = src.rfind("{% endblock %}")
    if last_endblock > 0:
        src = src[:last_endblock] + js + src[last_endblock:]
        print("JS handler added")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

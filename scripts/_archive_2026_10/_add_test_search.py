"""Add search filter to rate-list right panel."""
import io, os
path = os.path.join("templates", "test_settings", "_rate_dept_grid.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

# 1) add search input above the tests table (after panel title when selected_dept)
old_header = (
"      {% if not selected_dept %}" + nl +
"        <div class=\"rdg-info\">" + nl +
"          <i class=\"bi bi-info-circle\"></i><br>" + nl +
"          Click <strong>Detail</strong> on a department to see its tests." + nl +
"        </div>" + nl +
"      {% elif not dept_tests %}"
)
new_header = (
"      {% if selected_dept %}" + nl +
"        <div class=\"rdg-search\" style=\"padding:8px 10px;border-bottom:1px solid #212529;\">" + nl +
"          <input type=\"text\" id=\"testSearchBox\" placeholder=\"Search tests by name or code...\"" + nl +
"                 style=\"width:100%;padding:6px 10px;border:1px solid #212529;border-radius:6px;font-size:0.85rem;\"" + nl +
"                 onkeyup=\"filterTestRows(this.value)\">" + nl +
"        </div>" + nl +
"      {% endif %}" + nl +
"      {% if not selected_dept %}" + nl +
"        <div class=\"rdg-info\">" + nl +
"          <i class=\"bi bi-info-circle\"></i><br>" + nl +
"          Click <strong>Detail</strong> on a department to see its tests." + nl +
"        </div>" + nl +
"      {% elif not dept_tests %}"
)
if old_header in src:
    src = src.replace(old_header, new_header, 1)
    print("search box inserted")
else:
    print("HEADER ANCHOR MISS")

# 2) add data-search attr to each test row for filtering
old_row = "            <tr class=\"{% if not row.linked %}text-muted{% endif %}\">"
new_row = "            <tr class=\"test-row {% if not row.linked %}text-muted{% endif %}\" data-search=\"{{ (row.test.code ~ ' ' ~ row.test.name)|lower }}\">"
if old_row in src:
    src = src.replace(old_row, new_row, 1)
    print("row data-search added")
else:
    print("ROW ANCHOR MISS")

# 3) append filter JS at end of template
if "function filterTestRows" not in src:
    js = (
nl + "<script>" + nl +
"function filterTestRows(q) {" + nl +
"  var rows = document.querySelectorAll('.test-row');" + nl +
"  var needle = (q || '').toLowerCase().trim();" + nl +
"  var shown = 0;" + nl +
"  rows.forEach(function(r) {" + nl +
"    var hay = r.getAttribute('data-search') || '';" + nl +
"    if (!needle || hay.indexOf(needle) !== -1) { r.style.display = ''; shown++; }" + nl +
"    else { r.style.display = 'none'; }" + nl +
"  });" + nl +
"  var counter = document.getElementById('testSearchCount');" + nl +
"  if (counter) counter.textContent = shown;" + nl +
"}" + nl +
"</script>"
    )
    src = src + js
    print("filter JS appended")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

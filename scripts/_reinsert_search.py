"""Insert search box into right panel (after title)."""
import io, os
path = os.path.join("templates", "test_settings", "_rate_dept_grid.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

# Find the right-panel title (the one inside the second rdg-panel)
title_block = (
"      <div class=\"rdg-panel-title\">" + nl +
"        {% if selected_dept %}" + nl +
"          Selected Tests — {{ selected_dept.name }}" + nl +
"        {% else %}" + nl +
"          Selected Tests" + nl +
"        {% endif %}" + nl +
"      </div>"
)

if title_block not in src:
    # try without em dash
    title_block = (
"      <div class=\"rdg-panel-title\">" + nl +
"        {% if selected_dept %}" + nl +
"          Selected Tests - {{ selected_dept.name }}" + nl +
"        {% else %}" + nl +
"          Selected Tests" + nl +
"        {% endif %}" + nl +
"      </div>"
    )

if title_block in src and "testSearchBox" not in src:
    search = (
nl +
"      <div class=\"rdg-search\" style=\"padding:8px 10px;border-bottom:1px solid #212529;\">" + nl +
"        <input type=\"text\" id=\"testSearchBox\" placeholder=\"Search tests by name or code...\"" + nl +
"               style=\"width:100%;padding:6px 10px;border:1px solid #212529;border-radius:6px;font-size:0.85rem;\"" + nl +
"               onkeyup=\"filterTestRows(this.value)\">" + nl +
"      </div>"
    )
    src = src.replace(title_block, title_block + search, 1)
    print("search box inserted")
else:
    print("anchor MISS or already inserted")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

"""Insert search box right after the right-panel title div."""
import io, os
path = os.path.join("templates", "test_settings", "_rate_dept_grid.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

anchor = (
"        </div>" + nl +
"        {% if not selected_dept %}"
)
search = (
"        </div>" + nl +
"        <div class=\"rdg-search\" style=\"padding:8px 10px;border-bottom:1px solid #212529;background:#f8f9fa;\">" + nl +
"          <input type=\"text\" id=\"testSearchBox\" placeholder=\"Search tests...\"" + nl +
"                 style=\"width:100%;padding:6px 10px;border:1px solid #212529;border-radius:6px;font-size:0.85rem;\"" + nl +
"                 onkeyup=\"if(typeof filterTestRows==='function'){filterTestRows(this.value);}\">" + nl +
"        </div>" + nl +
"        {% if not selected_dept %}"
)

if "testSearchBox" not in src and anchor in src:
    src = src.replace(anchor, search, 1)
    print("search box inserted")
elif "testSearchBox" in src:
    print("already inserted")
else:
    print("anchor MISS")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

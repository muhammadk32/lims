"""Search box always visible in right panel; searches all tests in the rate list."""
import io, os
path = os.path.join("templates", "test_settings", "_rate_dept_grid.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

# 1) Always show search box (move it up before the dept-selected conditional)
old = (
"      <div class=\"rdg-panel-title\">" + nl +
"        {% if selected_dept %}" + nl +
"          Selected Tests — {{ selected_dept.name }}" + nl +
"        {% else %}" + nl +
"          Selected Tests" + nl +
"        {% endif %}" + nl +
"      </div>" + nl +
"      {% if selected_dept %}" + nl +
"        <div class=\"rdg-search\" style=\"padding:8px 10px;border-bottom:1px solid #212529;\">" + nl +
"          <input type=\"text\" id=\"testSearchBox\" placeholder=\"Search tests by name or code...\"" + nl +
"                 style=\"width:100%;padding:6px 10px;border:1px solid #212529;border-radius:6px;font-size:0.85rem;\"" + nl +
"                 onkeyup=\"filterTestRows(this.value)\">" + nl +
"        </div>" + nl +
"      {% endif %}"
)
new = (
"      <div class=\"rdg-panel-title\">" + nl +
"        {% if selected_dept %}" + nl +
"          Selected Tests — {{ selected_dept.name }}" + nl +
"        {% else %}" + nl +
"          Selected Tests" + nl +
"        {% endif %}" + nl +
"      </div>" + nl +
"      <div class=\"rdg-search\" style=\"padding:8px 10px;border-bottom:1px solid #212529;\">" + nl +
"        <input type=\"text\" id=\"testSearchBox\" placeholder=\"Search tests by name or code...\"" + nl +
"               style=\"width:100%;padding:6px 10px;border:1px solid #212529;border-radius:6px;font-size:0.85rem;\"" + nl +
"               onkeyup=\"filterTestRows(this.value)\">" + nl +
"      </div>"
)
if old in src:
    src = src.replace(old, new, 1)
    print("search box moved out of conditional")
else:
    print("anchor MISS — search box already positioned differently")
    # fallback: find the rdg-search div regardless of condition
    import re
    # just ensure it's outside the selected_dept conditional by removing wrapping {% if %}
    src = re.sub(r"\{%\s*if selected_dept\s*%\}\s*(<div class=\"rdg-search\".*?</div>)\s*\{%\s*endif\s*%\}",
                 r"\1", src, count=1, flags=re.DOTALL)
    print("fallback: moved search div out")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

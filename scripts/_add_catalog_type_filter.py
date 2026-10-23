"""Add type filter to catalog page."""
import io, os
path = os.path.join("templates", "test_settings", "_catalog.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

# 1) Add "Type" filter dropdown before the status filter
anchor = (
"  <div class=\"lt-field\">" + nl +
"    <label>Status</label>" + nl +
"    <select name=\"status\">"
)
new = (
"  <div class=\"lt-field\">" + nl +
"    <label>Type</label>" + nl +
"    <select name=\"type\">" + nl +
"      <option value=\"tests\" {% if type_filter == 'tests' %}selected{% endif %}>Tests + Panels</option>" + nl +
"      <option value=\"parameters\" {% if type_filter == 'parameters' %}selected{% endif %}>Parameters only</option>" + nl +
"      <option value=\"all\" {% if type_filter == 'all' %}selected{% endif %}>Show all</option>" + nl +
"    </select>" + nl +
"  </div>" + nl +
anchor
)
if 'name="type"' not in src and anchor in src:
    src = src.replace(anchor, new, 1)
    print("type filter added")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

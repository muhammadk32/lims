"""Add Packages link to topnav."""
import io, os
path = os.path.join("templates", "layout", "topnav.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

# add lts_active list — include packages
src = src.replace(
"['catalog','formats','categories','panels','units','bulk','previews','rates']",
"['catalog','formats','categories','panels','packages','units','bulk','previews','rates']")

# add menu item after Panels
anchor = (
"        <a href=\"{{ url_for('tests.index', tab='panels') }}\"" + nl +
"           class=\"dropdown-item {% if request.args.get('tab') == 'panels' %}active{% endif %}\">" + nl +
"          <i class=\"bi bi-collection\"></i> Panels" + nl +
"        </a>"
)
insert = anchor + nl + (
"        <a href=\"{{ url_for('tests.index', tab='packages') }}\"" + nl +
"           class=\"dropdown-item {% if request.args.get('tab') == 'packages' %}active{% endif %}\">" + nl +
"          <i class=\"bi bi-box-seam\"></i> Packages" + nl +
"        </a>"
)
if "tab='packages'" not in src:
    if anchor in src:
        src = src.replace(anchor, insert, 1)
        print("topnav item added")
    else:
        print("topnav anchor MISS")
else:
    print("already present")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

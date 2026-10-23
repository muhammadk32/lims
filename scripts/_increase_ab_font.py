"""Increase font size on antibiotics table rows."""
import io, os
path = os.path.join("templates", "settings", "antibiotics.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

add = (
"/* Bigger row + header fonts for antibiotics table */" + nl +
".admin-content table tbody td {" + nl +
"  font-size: 1rem !important;" + nl +
"  padding: 12px 14px !important;" + nl +
"  vertical-align: middle !important;" + nl +
"}" + nl +
".admin-content table thead th {" + nl +
"  font-size: 0.88rem !important;" + nl +
"  padding: 14px 14px !important;" + nl +
"}" + nl +
".admin-content table tbody td code {" + nl +
"  font-size: 0.92rem !important;" + nl +
"}" + nl
)

idx = src.find("</style>")
if "Bigger row + header fonts for antibiotics" not in src:
    src = src[:idx] + add + src[idx:]
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("font size increased")
else:
    print("already present")

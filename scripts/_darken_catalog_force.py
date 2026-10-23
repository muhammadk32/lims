"""Force dark borders on catalog table."""
import io, os
path = os.path.join("templates", "test_settings", "_catalog.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

# check what style block exists
import re

# remove old injected style block if present
old_style_start = src.find("<style>")
if old_style_start == 0:
    old_style_end = src.find("</style>", old_style_start) + len("</style>") + len(nl)
    src = src[old_style_end:]
    print("removed old style block")

# prepend higher-specificity CSS
new_style = (
"<style>" + nl +
"/* Catalog dark border overrides */" + nl +
"#content .lt-table, .lt-table { border-collapse:collapse !important; border:2px solid #212529 !important; border-radius:10px !important; overflow:hidden !important; }" + nl +
"#content .lt-table thead th, .lt-table thead th { background:#212529 !important; color:#fff !important; border-right:1px solid #444 !important; border-bottom:2px solid #212529 !important; }" + nl +
"#content .lt-table thead th:last-child, .lt-table thead th:last-child { border-right:none !important; }" + nl +
"#content .lt-table tbody td, .lt-table tbody td { border-bottom:1px solid #212529 !important; border-right:1px solid #212529 !important; }" + nl +
"#content .lt-table tbody td:last-child, .lt-table tbody td:last-child { border-right:none !important; }" + nl +
"#content .lt-table tbody tr:hover td, .lt-table tbody tr:hover td { background:#eaf2ff !important; }" + nl +
"#content .lt-table tbody tr:nth-child(even) td, .lt-table tbody tr:nth-child(even) td { background:#f7f9fc !important; }" + nl +
"/* Container border */" + nl +
"#content .lts-content > div, .lt-page { }" + nl +
"</style>" + nl
)
src = new_style + src

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("dark border CSS prepended")

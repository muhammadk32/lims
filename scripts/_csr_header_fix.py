"""Fix CSR table headers: larger font, centered, fix blur/borders."""
import io, os
path = os.path.join("modules", "billing", "templates", "billing", "report.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

old_css = """.csr-table thead th {
  background: #212529;
  color: #fff;
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 6px 8px;
  text-align: left;
  border-right: 1px solid #495057;
  white-space: nowrap;
}"""

new_css = """.csr-table thead th {
  background: #1a3d7c;
  color: #fff;
  font-size: 0.82rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding: 10px 12px;
  text-align: center;
  border-right: 1px solid #343a40;
  white-space: nowrap;
  vertical-align: middle;
}"""

if new_css in src:
    print("Header fix already applied")
elif old_css in src:
    src = src.replace(old_css, new_css)
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("Header CSS patched successfully")
else:
    print("Could not find old CSS block. Manual check needed.")

"""Replace .csr-table thead th block by line numbers, add center/print overrides."""
import io, os
path = os.path.join("modules", "billing", "templates", "billing", "report.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    lines = f.readlines()

# lines are 0-indexed; block is lines[222:234] (file lines 223-234)
start = None
for i, l in enumerate(lines):
    if l.strip() == ".csr-table thead th {":
        start = i
        break

if start is None:
    print("Header block not found")
else:
    # find closing brace of this block
    end = start
    while end < len(lines) and "}" not in lines[end]:
        end += 1
    new_block = [
        ".csr-table thead th {\n",
        "  background: #1a3d7c !important;\n",
        "  color: #fff !important;\n",
        "  font-size: 0.82rem !important;\n",
        "  font-weight: 700 !important;\n",
        "  text-transform: uppercase !important;\n",
        "  letter-spacing: 0.04em !important;\n",
        "  padding: 10px 12px !important;\n",
        "  text-align: center !important;\n",
        "  border-right: 1px solid #343a40 !important;\n",
        "  white-space: nowrap !important;\n",
        "  vertical-align: middle !important;\n",
        "}\n",
    ]
    lines[start:end+1] = new_block
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.writelines(lines)
    print(f"Patched header block at line {start+1}")

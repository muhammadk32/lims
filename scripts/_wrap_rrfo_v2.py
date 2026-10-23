"""Wrap _rrfo to strip HTML."""
import io, os
path = os.path.join("modules", "reports", "pdf", "results_table.py")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

# 1) rename import
src = src.replace(
"    resolve_range_for_order as _rrfo,",
"    resolve_range_for_order as _rrfo_raw,",
1)
print("import renamed")

# 2) insert wrapper right after the import block closes (first \n after line 5)
lines = src.split(nl)
# find line 5 (0-indexed = 4) and end of import block
insert_at = None
for i, line in enumerate(lines):
    if "resolve_range_for_order as _rrfo_raw" in line:
        # find next line that starts at column 0 (end of multi-line import)
        j = i + 1
        while j < len(lines) and (lines[j].startswith(" ") or lines[j].startswith(")")):
            j += 1
        insert_at = j
        break

if insert_at:
    wrapper = [
        "",
        "def _rrfo(test, order):",
        "    \"\"\"Wrap resolve_range_for_order: strip all HTML, return plain text.\"\"\"",
        "    try:",
        "        raw = _rrfo_raw(test, order) or '-'",
        "    except Exception:",
        "        return '-'",
        "    import re as _r",
        "    s = str(raw)",
        "    s = _r.sub(r'<[^>]+>', '', s)",
        "    s = _r.sub(r'\\s+', ' ', s).strip()",
        "    return s or '-'",
        "",
    ]
    lines = lines[:insert_at] + wrapper + lines[insert_at:]
    src = nl.join(lines)
    print("wrapper inserted after import block")
else:
    print("insert_at not found")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

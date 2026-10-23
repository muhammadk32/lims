"""Strengthen _rrfo wrapper: handle truncated tags + strip everything HTML."""
import io, os
path = os.path.join("modules", "reports", "pdf", "results_table.py")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

old = (
"def _rrfo(test, order):" + nl +
"    \"\"\"Wrap resolve_range_for_order: strip all HTML, return plain text.\"\"\"" + nl +
"    try:" + nl +
"        raw = _rrfo_raw(test, order) or '-'" + nl +
"    except Exception:" + nl +
"        return '-'" + nl +
"    import re as _r" + nl +
"    s = str(raw)" + nl +
"    s = _r.sub(r'<[^>]+>', '', s)" + nl +
"    s = _r.sub(r'\\s+', ' ', s).strip()" + nl +
"    return s or '-'"
)
new = (
"def _rrfo(test, order):" + nl +
"    \"\"\"Wrap resolve_range_for_order: strip all HTML, return plain text.\"\"\"" + nl +
"    try:" + nl +
"        raw = _rrfo_raw(test, order) or '-'" + nl +
"    except Exception:" + nl +
"        return '-'" + nl +
"    import re as _r" + nl +
"    s = str(raw)" + nl +
"    # Remove complete tags" + nl +
"    s = _r.sub(r'<[^>]*>', '', s)" + nl +
"    # Remove dangling truncated tags (unclosed < ...)" + nl +
"    s = _r.sub(r'<[^>]*$', '', s)" + nl +
"    # Remove any remaining < or > leftovers" + nl +
"    s = s.replace('<', '').replace('>', '')" + nl +
"    # Collapse whitespace" + nl +
"    s = _r.sub(r'\\s+', ' ', s).strip()" + nl +
"    return s or '-'"
)
if old in src:
    src = src.replace(old, new, 1)
    print("wrapper strengthened")
else:
    print("anchor MISS")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

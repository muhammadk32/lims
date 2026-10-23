"""Wrap _rrfo in results_table.py to always return plain text."""
import io, os
path = os.path.join("modules", "reports", "pdf", "results_table.py")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

# 1) At the import of _rrfo, rename + wrap
if "def _rrfo_safe" not in src:
    # find existing import
    old_import = "from modules.tests.ranges import resolve_range_for_order as _rrfo"
    if old_import in src:
        # remove the direct alias, add safe wrapper
        src = src.replace(old_import, "from modules.tests.ranges import resolve_range_for_order as _rrfo_raw", 1)

        # insert wrapper after imports block
        marker = "\ndef _results_table"
        wrapper = (
nl +
"def _rrfo(test, order):" + nl +
"    \"\"\"Wrap resolve_range_for_order: strip ALL HTML, return plain text.\"\"\"" + nl +
"    try:" + nl +
"        raw = _rrfo_raw(test, order) or '-'" + nl +
"    except Exception:" + nl +
"        return '-'" + nl +
"    import re as _r" + nl +
"    s = str(raw)" + nl +
"    s = _r.sub(r'<[^>]+>', '', s)" + nl +
"    s = _r.sub(r'\\s+', ' ', s).strip()" + nl +
"    return s or '-'" + nl +
nl
        )
        if marker in src:
            src = src.replace(marker, wrapper + marker, 1)
            print("_rrfo wrapper installed")
        else:
            print("marker MISS")
    else:
        print("import anchor MISS")
else:
    print("already wrapped")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

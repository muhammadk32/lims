"""Fix _pick to sanitize both return values."""
import io, os
path = os.path.join("modules", "reports", "pdf", "results_table.py")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

old = "            return a if a else (b if tpl else None)"
new = "            return _sanitize_para(a if a else (b if tpl else None))"
if old in src:
    src = src.replace(old, new, 1)
    print("_pick wrapped")
else:
    print("anchor MISS")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

"""Remove duplicate def new_order(): line."""
import io, os
path = os.path.join("modules", "orders", "routes.py")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

dup = "def new_order():" + nl + "def new_order():"
if dup in src:
    src = src.replace(dup, "def new_order():", 1)
    print("duplicate removed")
else:
    print("dup not found — check lines 124-130")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

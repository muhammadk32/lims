"""Stop syncRateManagedFields from resetting value; only disable."""
import io, os
path = os.path.join("modules", "orders", "templates", "orders", "new.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

old = "        if (el.value !== '0') el.value = '0';"
new = "        // do not reset value — leaving it alone so rate-list mirror can write"
if old in src:
    src = src.replace(old, new, 1)
    print("reset removed")
else:
    print("anchor MISS")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

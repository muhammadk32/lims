"""Guard rateListHint access after removal."""
import io, os
path = os.path.join("modules", "orders", "templates", "orders", "new.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

old = (
"    var hint = document.getElementById('rateListHint');" + nl +
"    if (hint) hint.style.display = labSelected ? '' : 'none';"
)
new = "    // hint element removed — label handles it"
if old in src:
    src = src.replace(old, new, 1)
    print("hint guard applied")
else:
    print("already ok")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

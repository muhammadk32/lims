"""Hide ** junk and <Type> from rate list export."""
import io, os
path = os.path.join("modules", "tests", "routes.py")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

old = "            if t.id in child_ids: continue"
new = (
"            if t.id in child_ids: continue" + nl +
"            # hide **-prefixed junk names and '<Type>' placeholders" + nl +
"            nm = (t.name or '').strip()" + nl +
"            if nm.startswith('**'): continue" + nl +
"            if nm in ('<Type>', ''): continue"
)

# apply in export route (specific context)
if "nm.startswith('**')" not in src:
    if old in src:
        src = src.replace(old, new, 1)
        print("filter added")
    else:
        print("ANCHOR MISS")
else:
    print("already")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

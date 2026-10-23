"""Export: skip zero-price non-parent, non-package tests."""
import io, os
path = os.path.join("modules", "tests", "routes.py")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

old = (
"            nm = (t.name or '').strip()" + nl +
"            if nm.startswith('**'): continue" + nl +
"            if nm in ('<Type>', ''): continue"
)
new = (
"            nm = (t.name or '').strip()" + nl +
"            if nm.startswith('**'): continue" + nl +
"            if nm in ('<Type>', ''): continue" + nl +
"            # skip 0-price non-parent, non-package rows (AdamLab label/analyte junk)" + nl +
"            price_v = float(t.price or 0)" + nl +
"            if price_v == 0 and not t.is_panel:" + nl +
"                # allow if it's a package" + nl +
"                if (t.result_format or '').lower() != 'package':" + nl +
"                    continue"
)

if "skip 0-price non-parent" not in src:
    if old in src:
        src = src.replace(old, new, 1)
        print("zero-price filter added")
    else:
        print("ANCHOR MISS")
else:
    print("already")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

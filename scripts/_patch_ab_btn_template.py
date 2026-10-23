"""Direct CSS override inside antibiotics template — beats specificity."""
import io, os
path = os.path.join("templates", "settings", "antibiotics.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

old_sm = ".ab-btn-sm { padding: 2px 8px; font-size: 0.68rem; height: 22px; line-height: 1.4; }"
new_sm = (
".ab-btn-sm { padding: 6px 12px; font-size: 0.78rem; height: 32px; line-height: 1; border-radius: 6px;" + nl +
"             display: inline-flex; align-items: center; gap: 4px; font-weight: 700; text-transform: uppercase;" + nl +
"             letter-spacing: 0.03em; border-width: 2px; box-sizing: border-box; min-width: 32px; justify-content: center; }" + nl +
".ab-actions .ab-btn-sm i { font-size: 0.9rem; }" + nl +
".ab-actions .ab-btn-sm:has(>i:only-child) { width: 32px; padding: 0; min-width: 32px; }"
)

if old_sm in src:
    src = src.replace(old_sm, new_sm, 1)
    print(".ab-btn-sm replaced")
else:
    print("anchor MISS")

# Also patch status pill
old_status = ".ab-status"
if old_status in src:
    # strengthen .ab-status padding/font
    import re
    src = re.sub(r'\.ab-status\s*\{[^}]*\}',
        ".ab-status { display: inline-block; padding: 6px 14px; font-size: 0.76rem; font-weight: 800;" + nl +
        "             letter-spacing: 0.05em; text-transform: uppercase; border-radius: 6px; line-height: 1.1; }",
        src, count=1)
    print(".ab-status reinforced")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

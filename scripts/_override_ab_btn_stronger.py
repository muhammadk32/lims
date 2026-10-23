"""Patch antibiotics template: override admin_theme.css rule #2."""
import io, os
path = os.path.join("templates", "settings", "antibiotics.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

# replace the existing .ab-actions .ab-btn-sm:has rule with a stronger one
old = ".ab-actions .ab-btn-sm:has(>i:only-child) { width: 32px; padding: 0; min-width: 32px; }"
new = (
".ab-actions .ab-btn-sm:has(>i:only-child) { width: 32px !important; height: 32px !important; padding: 0 !important; min-width: 32px !important; }" + nl +
".ab-actions .ab-btn-sm { padding: 6px 12px !important; height: 32px !important; min-height: 32px !important; font-size: 0.78rem !important; }" + nl +
".ab-actions button.ab-btn { border-radius: 6px !important; }"
)

if old in src:
    src = src.replace(old, new, 1)
    print("stronger override added")
else:
    # try to find existing has rule (may have different indentation)
    import re
    m = re.search(r'\.ab-actions \.ab-btn-sm:has\(>i:only-child\) \{[^}]*\}', src)
    if m:
        src = src[:m.start()] + new + src[m.end():]
        print("replaced via regex")
    else:
        # append at end of style
        idx = src.find("</style>")
        src = src[:idx] + new + nl + src[idx:]
        print("appended")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

"""Delete all but the grid .dl-summary; also delete .value.success/.danger overrides."""
import io, os
path = os.path.join("modules", "orders", "templates", "orders", "list.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    lines = f.readlines()

# 1) Remove lines: .dl-summary .value.success / .value.danger / [data-bs-theme] ones (244-253 region)
# Safer: find them by content.
drop_content = [
    ".dl-summary .value.success { color: #146c43; }",
    ".dl-summary .value.danger  { color: #b02a37; }",
    '[data-bs-theme="dark"] .dl-summary { border-color: #000; }',
    '[data-bs-theme="dark"] .dl-summary .value.success { color: #34d399; }',
    '[data-bs-theme="dark"] .dl-summary .value.danger  { color: #f87171; }',
]
lines = [l for l in lines if l.strip() not in [c.strip() for c in drop_content]]

# 2) Remove old duplicated .dl-summary block at ~337 (has "display: flex !important; flex-wrap: wrap")
out = []
i = 0
while i < len(lines):
    # detect start of the flex version
    if lines[i].strip() == ".dl-summary {" and i+1 < len(lines) and "display: flex !important" in lines[i+1]:
        # skip until we exit the block (next blank line after the closing "}")
        depth = 0
        j = i
        while j < len(lines):
            depth += lines[j].count("{") - lines[j].count("}")
            if j > i and depth <= 0:
                break
            j += 1
        # find end of the entire "FOOTER SUMMARY: BORDERS + COLORED FIELDS" section
        k = j
        # skip until we hit "/* ===== " or a blank line 2 in a row
        # Safer: skip until the next marker comment we recognize
        while k < len(lines) and "/* ===== ABSOLUTE FOOTER SHADING FIX ===== */" not in lines[k]:
            k += 1
        i = k
        continue
    out.append(lines[i])
    i += 1

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.writelines(out)
print("Removed conflicting .dl-summary blocks. Only grid version remains.")

"""Remove duplicate .dl-summary CSS blocks, keep only the final grid one."""
import io, os, re
path = os.path.join("modules", "orders", "templates", "orders", "list.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    lines = f.readlines()

# Kill everything from line 241..266 (0-index 240..266) and 366..425 (0-index 365..425)
# Do the higher range first so lower indices stay valid.
# Recompute by finding markers.
def find_block(lines, start_marker, end_marker_pattern):
    start = None
    for i, l in enumerate(lines):
        if start_marker in l:
            start = i
            break
    if start is None:
        return None, None
    end = start
    depth = l.count("{") - l.count("}")
    depth = lines[start].count("{") - lines[start].count("}")
    # walk until depth returns to 0
    for j in range(start, len(lines)):
        depth += lines[j].count("{") - lines[j].count("}")
        if depth <= 0 and j > start:
            end = j
            break
    return start, end

# 1) Remove the ORIGINAL .dl-summary block (line 241) — it has the flex override
# Find unique marker: ".dl-summary .stat { display: flex; justify-content: space-between;"
target_line = None
for i, l in enumerate(lines):
    if ".dl-summary .stat { display: flex; justify-content: space-between;" in l:
        target_line = i
        break

if target_line is not None:
    # Walk backwards to the opening ".dl-summary {"
    start = target_line
    while start > 0 and ".dl-summary {" not in lines[start]:
        start -= 1
    # Walk forward to the last rule in that block (up to dark theme lines)
    end = target_line
    while end < len(lines) and "dl-summary" in lines[end]:
        end += 1
    # Trim one extra line to catch the closing brace
    if end < len(lines) and lines[end].strip() == "":
        end += 1
    del lines[start:end]
    print(f"Removed original .dl-summary block (lines ~{start+1}-{end})")

# 2) Remove the SECOND duplicated block if it exists
# Marker: "/* ===== FOOTER SUMMARY: BORDERS + COLORED FIELDS ===== */"
markers = [
    "/* ===== FOOTER SUMMARY: BORDERS + COLORED FIELDS ===== */",
    "/* ===== FOOTER ROW STYLING ===== */",
]
for m in markers:
    start = None
    for i, l in enumerate(lines):
        if m in l:
            start = i
            break
    if start is not None:
        # Find end: next "/* ===== " marker or end of style
        end = start + 1
        while end < len(lines) and "/* ===== " not in lines[end] and "</style>" not in lines[end]:
            end += 1
        del lines[start:end]
        print(f"Removed block starting at {m[:40]}...")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.writelines(lines)
print("Cleaned duplicate .dl-summary CSS blocks.")

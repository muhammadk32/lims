"""Remove the old 1% width rule."""
import io, os
path = os.path.join("modules", "patients", "templates", "patients", "history.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

# find the first .ph-table th.actions-col block and remove it
import re
pattern = r'\.ph-table th\.actions-col,\s*\.ph-table td\.actions-cell\s*\{[^}]*\}'
matches = re.findall(pattern, src)
print(f"matches: {len(matches)}")

if len(matches) >= 1:
    # remove only the FIRST one (the 1% width one)
    src = re.sub(pattern, '', src, count=1, flags=re.DOTALL)
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("removed old 1% rule")

# also remove duplicate `.ph-row-actions` (line 255 may override line 187)
pattern2 = r'\.ph-row-actions\s*\{[^}]*\}'
matches2 = re.findall(pattern2, src)
print(f"ph-row-actions blocks: {len(matches2)}")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

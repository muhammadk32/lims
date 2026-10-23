"""Remove duplicate panel header (Outsourced Laboratories)."""
import io, os, re
path = os.path.join("templates", "settings", "laboratories.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

# Match the panel head block for OUTSOURCED LABORATORIES
pattern = (
r'<header class="lab-panel-head" onclick="document\.getElementById\(\'panel-outsourced\'\)\.classList\.toggle\(\'collapsed\'\)">.*?</header>\s*'
)
count = len(re.findall(pattern, src, flags=re.DOTALL))
print(f"matches: {count}")

if count >= 1:
    src = re.sub(pattern, '', src, count=1, flags=re.DOTALL)
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("outsourced panel header removed")
else:
    print("no match")

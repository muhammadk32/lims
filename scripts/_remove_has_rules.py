"""Remove aggressive :has(> i:only-child) rules from admin_theme.css."""
import io, os, re
path = os.path.join("static", "css", "admin_theme.css")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

# Remove all rules with :has(> i:only-child)
pattern = r'[^{}]*:has\(\s*>\s*i:only-child\s*\)[^{]*\{[^}]*\}'
before = len(src)
src = re.sub(pattern, '', src, flags=re.DOTALL)
after = len(src)
print(f"removed {before - after} chars of :has() rules")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

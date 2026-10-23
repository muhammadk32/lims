"""Fix: admin-content → app-content (actual class in base.html)."""
import io, os
path = os.path.join("static", "css", "admin_theme.css")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

if ".admin-content" in src:
    src = src.replace(".admin-content", ".app-content")
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("admin-content → app-content in admin_theme.css")

# same for antibiotics template
path2 = os.path.join("templates", "settings", "antibiotics.html")
with io.open(path2, "r", encoding="utf-8", newline="") as f:
    src2 = f.read()
if ".admin-content" in src2:
    src2 = src2.replace(".admin-content", ".app-content")
    with io.open(path2, "w", encoding="utf-8", newline="") as f:
        f.write(src2)
    print("admin-content → app-content in antibiotics.html")

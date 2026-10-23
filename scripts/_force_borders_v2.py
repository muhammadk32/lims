"""Darken all table borders in rate list export."""
import io, os
path = os.path.join("templates", "test_settings", "_rate_list_export.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

# Replace ALL border colors on rle-table with dark
src = src.replace("border:2px solid #1a3d7c;\r\n  border-radius:12px; overflow:hidden;",
                  "border:2px solid #212529 !important;\r\n  border-radius:12px; overflow:hidden;")
src = src.replace("border-right:1px solid rgba(255,255,255,0.2);",
                  "border-right:1px solid #212529 !important;")
src = src.replace("padding:7px 12px; border-bottom:1px solid #dee2e6;\r\n  border-right:1px solid #dee2e6;",
                  "padding:7px 12px; border-bottom:1px solid #212529 !important;\r\n  border-right:1px solid #212529 !important;")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("dark borders applied")

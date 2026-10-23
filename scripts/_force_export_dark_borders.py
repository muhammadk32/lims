"""Force dark borders on rate export table."""
import io, os
path = os.path.join("templates", "test_settings", "_rate_list_export.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

# 1) table outer border → !important
src = src.replace(
".rle-table {" + "\r\n" +
"  width:100%; border-collapse:separate; border-spacing:0;" + "\r\n" +
"  font-size:0.85rem; border:2px solid #1a3d7c;" + "\r\n" +
"  border-radius:12px; overflow:hidden;" + "\r\n" +
"}",
".rle-table {" + "\r\n" +
"  width:100%; border-collapse:separate !important; border-spacing:0 !important;" + "\r\n" +
"  font-size:0.85rem; border:2px solid #212529 !important;" + "\r\n" +
"  border-radius:12px; overflow:hidden;" + "\r\n" +
"}")

# 2) cell borders → !important + darker
src = src.replace(
".rle-table tbody td {" + "\r\n" +
"  padding:7px 12px; border-bottom:1px solid #dee2e6;" + "\r\n" +
"  border-right:1px solid #dee2e6;" + "\r\n" +
"  vertical-align:middle;" + "\r\n" +
"}",
".rle-table tbody td {" + "\r\n" +
"  padding:7px 12px; border-bottom:1px solid #212529 !important;" + "\r\n" +
"  border-right:1px solid #212529 !important;" + "\r\n" +
"  vertical-align:middle;" + "\r\n" +
"}")

# 3) header th borders
src = src.replace(
"  border-right:1px solid rgba(255,255,255,0.2);" + "\r\n" +
"}",
"  border-right:1px solid #212529 !important; border-bottom:2px solid #212529 !important;" + "\r\n" +
"}")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("borders forced")

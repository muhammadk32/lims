"""Darken report table borders."""
import io, os
path = os.path.join("templates", "test_settings", "_rate_list_export.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

src = src.replace(
".rle-table { width:100%; border-collapse:collapse; font-size:0.82rem; }",
".rle-table { width:100%; border-collapse:collapse; font-size:0.82rem; border:2px solid #212529; border-radius:8px; overflow:hidden; }")

src = src.replace(
".rle-table tbody td { padding:4px 8px; border-bottom:1px solid #ced4da; vertical-align:middle; }",
".rle-table tbody td { padding:4px 8px; border-bottom:1px solid #212529; border-right:1px solid #212529; vertical-align:middle; }")

src = src.replace(
".rle-table thead th { background:#212529; color:#fff; padding:7px 8px; text-align:left; font-size:0.76rem; text-transform:uppercase; }",
".rle-table thead th { background:#212529; color:#fff; padding:7px 8px; text-align:left; font-size:0.76rem; text-transform:uppercase; border-right:1px solid #444; }\n.rle-table thead th:last-child, .rle-table tbody td:last-child { border-right:none; }")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("borders darkened")

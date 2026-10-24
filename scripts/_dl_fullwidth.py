"""Remove max-width so Daily Ledger fits the whole screen."""
import io, os
path = os.path.join("modules", "orders", "templates", "orders", "list.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

# Remove previous fit blocks
for marker in [
    "/* ===== FIT TO SCREEN (MATCHING POLISHED PAGES) ===== */",
    "/* ===== EXPAND PAGE WIDTH ===== */",
    "/* ===== POLISHED THEME ===== */", # will re-add clean below
]:
    if marker in src:
        start = src.find(marker)
        end = src.find("</style>", start)
        src = src[:start] + src[end:]

add = """
/* ===== FULL-WIDTH FIT ===== */
.dl-page {
    max-width: 100% !important;
    width: 100% !important;
    margin: 0 !important;
    padding: 16px 24px 40px !important;
    box-sizing: border-box !important;
    overflow-x: hidden !important;
}
.dl-card, .dl-table {
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
}
/* Let columns size themselves to content, no forced widths */
.dl-table th, .dl-table td {
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}
"""

idx = src.rfind("</style>")
if idx > 0:
    src = src[:idx] + add + src[idx:]
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("Full-width fit applied.")

"""Set Daily Ledger page width to match other polished pages (1400px centered)."""
import io, os
path = os.path.join("modules", "orders", "templates", "orders", "list.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== FIT TO SCREEN (MATCHING POLISHED PAGES) ===== */
.dl-page {
    max-width: 1400px !important;
    margin: 0 auto !important;
    padding: 16px 24px 40px !important;
    box-sizing: border-box !important;
}
"""

idx = src.rfind("</style>")
if idx > 0:
    if "/* ===== FIT TO SCREEN (MATCHING POLISHED PAGES) ===== */" not in src:
        src = src[:idx] + add + src[idx:]
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(src)
        print("Page width set to 1400px centered.")
    else:
        print("Already applied.")

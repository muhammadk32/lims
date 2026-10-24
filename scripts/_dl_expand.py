"""Expand Daily Ledger page width."""
import io, os
path = os.path.join("modules", "orders", "templates", "orders", "list.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== EXPAND PAGE WIDTH ===== */
.dl-page {
    max-width: 100% !important;
    padding: 16px 32px 40px !important;
}
"""

idx = src.rfind("</style>")
if idx > 0:
    if "/* ===== EXPAND PAGE WIDTH ===== */" not in src:
        src = src[:idx] + add + src[idx:]
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(src)
        print("Page width expanded.")
    else:
        print("Already applied.")

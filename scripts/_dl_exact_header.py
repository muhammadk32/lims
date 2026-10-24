"""Copy the exact header font from Reports page to Daily Ledger headers."""
import io, os
path = os.path.join("modules", "orders", "templates", "orders", "list.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== EXACT HEADER FONT COPY ===== */
.dl-table thead th {
    font-family: 'Segoe UI', Arial, sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 800 !important;       /* Extra bold like Reports */
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
    color: #fff !important;
    background: linear-gradient(180deg, #0d6efd 0%, #1a3d7c 100%) !important;
    padding: 14px 12px !important;     /* Restore the original padding */
    text-align: center !important;
    white-space: nowrap !important;
    border-bottom: 2px solid #212529 !important;
    border-right: 1px solid #212529 !important;
}
"""

idx = src.rfind("</style>")
if idx > 0:
    # Remove the previous "REFINE" block that made it too small
    if "/* ===== REFINE TABLE TYPOGRAPHY ===== */" in src:
        start = src.find("/* ===== REFINE TABLE TYPOGRAPHY ===== */")
        src = src[:start] + add + src[idx:]
    else:
        src = src[:idx] + add + src[idx:]

    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("Exact header font applied.")

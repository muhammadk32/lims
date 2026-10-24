"""Style the Daily Ledger footer (tfoot) to match table."""
import io, os
path = os.path.join("modules", "orders", "templates", "orders", "list.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== FOOTER ROW STYLING ===== */
.dl-table tfoot td {
    background: #f8f9fa !important;
    border-top: 2px solid #212529 !important;
    border-bottom: 2px solid #212529 !important;
    border-right: 1px solid #212529 !important;
    padding: 12px 8px !important;
    font-size: 0.85rem !important;
    font-weight: 800 !important;
    text-transform: uppercase !important;
    color: #212529 !important;
    white-space: nowrap !important;
}
.dl-table tfoot td:last-child {
    border-right: none !important;
}
/* Remove the weird container border if it has one */
.dl-summary, .dl-tfoot-container, .table-footer {
    border: none !important;
    background: transparent !important;
}
"""

idx = src.rfind("</style>")
if idx > 0:
    if "/* ===== FOOTER ROW STYLING ===== */" not in src:
        src = src[:idx] + add + src[idx:]
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(src)
        print("Footer row styled.")
    else:
        print("Already applied.")

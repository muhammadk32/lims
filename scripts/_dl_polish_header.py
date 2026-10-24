"""Polish Daily Ledger header and filter area to match the rest."""
import io, os
path = os.path.join("modules", "orders", "templates", "orders", "list.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== POLISHED HEADER AND FILTER ===== */
.dl-header {
    display: flex !important;
    justify-content: space-between !important;
    align-items: flex-end !important;
    background: linear-gradient(135deg, #1a3d7c 0%, #0d6efd 100%) !important;
    border: 2px solid #212529 !important;
    border-radius: 10px !important;
    padding: 16px 20px !important;
    margin-bottom: 16px !important;
    color: #fff !important;
}
.dl-title {
    font-size: 1.25rem !important;
    font-weight: 700 !important;
    margin: 0 !important;
    text-transform: uppercase !important;
    color: #fff !important;
}
.dl-title i { color: #fff !important; }
.dl-subtitle {
    font-size: 0.85rem !important;
    color: #dbeafe !important;
    font-family: Consolas, Monaco, monospace !important;
}
.dl-count {
    font-size: 0.85rem !important;
    color: #dbeafe !important;
    font-family: Consolas, Monaco, monospace !important;
}

/* Filter area */
.dl-filter {
    background: #fff !important;
    border: 2px solid #212529 !important;
    border-radius: 8px !important;
    padding: 14px 16px !important;
    margin-bottom: 16px !important;
}
.dl-filter::before { content: none !important; display: none !important; } /* Remove the old "+ FILTERS" bar */

.dl-field label {
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    color: #6c757d !important;
    text-transform: uppercase !important;
}

/* Search inputs inside filter */
.dl-filter input, .dl-filter select {
    border: 1px solid #ced4da !important;
    border-radius: 4px !important;
    height: 38px !important;
}
"""

idx = src.rfind("</style>")
if idx > 0:
    if "/* ===== POLISHED HEADER AND FILTER ===== */" not in src:
        src = src[:idx] + add + src[idx:]
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(src)
        print("Header and filter polished.")

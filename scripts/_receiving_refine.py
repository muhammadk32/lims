"""Refine receiving.html to exactly match Reports page."""
import io, os
path = os.path.join("modules", "lab", "templates", "lab", "receiving.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== FINAL MATCH TO REPORTS THEME ===== */

/* Header */
.sr-header {
    background: linear-gradient(135deg, #1a3d7c 0%, #0d6efd 100%) !important;
    border: none !important; /* Reports has no dark border on header */
    border-radius: 10px !important;
    padding: 16px 20px !important;
    margin-bottom: 16px !important;
    color: #fff !important;
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
}

/* Filter Box */
.sr-filter {
    border: 1px solid #dee2e6 !important; /* Light border like Reports */
    border-radius: 8px !important;
    padding: 14px 16px !important;
    margin-bottom: 16px !important;
    background: #fff !important;
}

/* Yellow Band */
.sr-band {
    background: #fff8e1 !important;
    border: 1px solid #ffe69c !important; /* Soft yellow border */
    color: #664d03 !important;
    font-weight: 700 !important;
    padding: 10px 16px !important;
    border-radius: 8px !important;
    margin-bottom: 0 !important;
}

/* Table Wrapper */
.sr-card {
    border: 2px solid #212529 !important; /* Dark outer border */
    border-radius: 8px !important;
    overflow: hidden !important;
    background: #fff !important;
}
.sr-table {
    border: none !important;
    border-collapse: collapse !important;
    width: 100% !important;
}

/* Table Header - Blue, centered, no heavy dark borders on cells */
.sr-table thead th {
    background: #1a3d7c !important;
    color: #fff !important;
    font-size: 0.82rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
    padding: 12px 12px !important;
    text-align: center !important;
    border: 1px solid #343a40 !important; /* Subtle border between headers */
    border-top: none !important;
}

/* Table Body - light borders, alternating rows */
.sr-table tbody td {
    padding: 10px 12px !important;
    border-bottom: 1px solid #dee2e6 !important; /* Light borders */
    border-right: 1px solid #f1f3f5 !important;
    font-size: 0.9rem !important;
    background: #fff !important;
}
.sr-table tbody td:last-child { border-right: none !important; }
.sr-table tbody tr:nth-child(even) td { background: #fbfcfd !important; }
.sr-table tbody tr:hover td { background: #eaf2ff !important; }
"""

idx = src.rfind("</style>")
if idx > 0:
    if "/* ===== FINAL MATCH TO REPORTS THEME ===== */" not in src:
        src = src[:idx] + add + src[idx:]
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(src)
        print("Receiving page refined to match Reports.")
    else:
        print("Already applied.")

"""Restore dark borders on the table."""
import io, os
path = os.path.join("modules", "lab", "templates", "lab", "receiving.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== FORCE VISIBLE BORDERS ===== */
.sr-card {
    border: none !important;
    border-radius: 0 !important;
    overflow: visible !important;
    background: transparent !important;
    padding: 0 !important;
}

.sr-table {
    width: 100% !important;
    border-collapse: collapse !important;
    border: 2px solid #212529 !important; /* Dark outer border */
    margin: 0 !important;
}

.sr-table thead th {
    border: 1px solid #212529 !important; /* Dark borders on headers */
    border-bottom: 2px solid #212529 !important;
    background: #1a3d7c !important;
    color: #fff !important;
    text-align: center !important;
}

.sr-table tbody td {
    border: 1px solid #212529 !important; /* Dark borders on data cells */
    background: #fff !important;
}

/* Keep the hover effect clean */
.sr-table tbody tr:hover td {
    background: #eaf2ff !important;
}
"""

idx = src.rfind("</style>")
if idx > 0:
    if "/* ===== FORCE VISIBLE BORDERS ===== */" not in src:
        src = src[:idx] + add + src[idx:]
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(src)
        print("Dark borders forced on table.")
    else:
        print("Already applied.")

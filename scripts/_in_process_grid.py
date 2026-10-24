"""Force visible dark borders on EVERY cell, row, and column."""
import io, os
path = os.path.join("modules", "lab", "templates", "lab", "in_process.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== FORCE DARK GRID BORDERS ON ALL CELLS ===== */
.tip-card {
    border: 2px solid #212529 !important;
    border-radius: 6px !important;
    overflow: hidden !important;
    padding: 0 !important;
}

.tip-table {
    border-collapse: collapse !important;
    width: 100% !important;
    margin: 0 !important;
    border: 2px solid #212529 !important;
}

.tip-table thead th {
    border: 1px solid #212529 !important; /* Dark border on ALL header cells */
    background: #1a3d7c !important;
    color: #fff !important;
    text-align: center !important;
    padding: 12px 8px !important;
}

.tip-table tbody td {
    border: 1px solid #212529 !important; /* Dark border on ALL body cells */
    padding: 10px 12px !important;
    background: #fff !important;
}
"""

idx = src.rfind("</style>")
if idx > 0:
    if "/* ===== FORCE DARK GRID BORDERS ON ALL CELLS ===== */" not in src:
        src = src[:idx] + add + src[idx:]
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(src)
        print("Grid borders applied to all cells.")
    else:
        print("Already applied.")

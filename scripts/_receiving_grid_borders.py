"""Apply strict dark grid borders around the table."""
import io, os
path = os.path.join("modules", "lab", "templates", "lab", "receiving.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== STRICT GRID BORDERS ===== */
.sr-card {
    border: none !important; /* Remove from card to prevent clipping */
    overflow: visible !important;
    background: transparent !important;
}

.sr-table {
    border: 2px solid #212529 !important; /* Dark outer box */
    border-collapse: collapse !important;
}

/* Dark borders on every cell, including headers */
.sr-table th, 
.sr-table td {
    border: 1px solid #212529 !important;
}

/* Re-apply the gradient to headers so it stays professional */
.sr-table thead th {
    background: linear-gradient(180deg, #0d6efd 0%, #1a3d7c 100%) !important;
    color: #fff !important;
    border-bottom: 2px solid #212529 !important;
}
"""

idx = src.rfind("</style>")
if idx > 0:
    if "/* ===== STRICT GRID BORDERS ===== */" not in src:
        src = src[:idx] + add + src[idx:]
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(src)
        print("Dark grid borders applied.")
    else:
        print("Already applied.")

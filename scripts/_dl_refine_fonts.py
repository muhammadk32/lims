"""Fix table font size and padding to match Reports."""
import io, os
path = os.path.join("modules", "orders", "templates", "orders", "list.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== REFINE TABLE TYPOGRAPHY ===== */
.dl-table thead th {
    font-size: 0.72rem !important; /* Smaller header to fit */
    padding: 10px 6px !important; /* Tighter horizontal padding */
    white-space: nowrap !important; /* Force single line */
}

.dl-table tbody td {
    font-size: 0.82rem !important; /* Smaller body text */
    padding: 8px 6px !important; /* Tighter padding */
}

/* Shaded Status and Payment columns */
.dl-table tbody td:nth-child(11) { /* Status */
    background-color: #eef4ff !important;
    font-weight: 700 !important;
}
.dl-table tbody td:nth-child(12) { /* Payment */
    background-color: #eef4ff !important;
    font-weight: 700 !important;
}
"""

idx = src.rfind("</style>")
if idx > 0:
    if "/* ===== REFINE TABLE TYPOGRAPHY ===== */" not in src:
        src = src[:idx] + add + src[idx:]
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(src)
        print("Table typography refined.")
    else:
        print("Already applied.")

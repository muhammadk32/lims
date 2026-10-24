"""Fix missing outer border and header gaps."""
import io, os
path = os.path.join("modules", "lab", "templates", "lab", "in_process.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== ABSOLUTE BORDER FIX ===== */
.tip-card {
    border: 2px solid #212529 !important;
    border-radius: 8px !important;
    overflow: hidden !important;
    background: #fff !important;
}

.tip-table {
    border: none !important;
    border-collapse: collapse !important;
    width: 100% !important;
    margin: 0 !important;
}

.tip-table thead th {
    border: 1px solid #212529 !important;
    border-top: none !important; /* Let the card border act as the top border */
    border-left: none !important; /* Let the card border act as the left border */
    text-align: center !important;
    background: #1a3d7c !important;
    color: #fff !important;
    padding: 12px 8px !important;
}
.tip-table thead th:first-child {
    border-left: 1px solid #212529 !important; /* Ensure inner vertical lines show */
}
.tip-table thead th:last-child {
    border-right: none !important;
}

.tip-table tbody td {
    border: 1px solid #dee2e6 !important;
    border-top: none !important;
    border-left: none !important;
    padding: 10px 12px !important;
    background: #fff !important;
}
.tip-table tbody td:first-child {
    border-left: 1px solid #dee2e6 !important; /* Vertical lines for body */
}
.tip-table tbody td:last-child {
    border-right: none !important;
}
.tip-table tbody tr:last-child td {
    border-bottom: none !important;
}
"""

idx = src.rfind("</style>")
if idx > 0:
    if "/* ===== ABSOLUTE BORDER FIX ===== */" not in src:
        src = src[:idx] + add + src[idx:]
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(src)
        print("Absolute borders applied.")
    else:
        print("Already applied.")

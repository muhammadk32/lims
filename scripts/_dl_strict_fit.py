"""Force table to fit 100% width without overflow."""
import io, os
path = os.path.join("modules", "orders", "templates", "orders", "list.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== STRICT FIT WITHIN SCREEN ===== */
.dl-page {
    max-width: 100% !important;
    padding: 16px 24px 40px !important;
    overflow-x: hidden !important;
}

.dl-card {
    border: none !important;
    overflow: hidden !important; /* Prevent inner table from spilling out */
    width: 100% !important;
}

.dl-table {
    width: 100% !important;
    table-layout: fixed !important; /* Force columns to obey container */
    border-collapse: separate !important;
    border-spacing: 0 !important;
    border: 2px solid #212529 !important;
    border-radius: 8px 8px 0 0 !important;
}

/* Reduce padding to make room for text */
.dl-table thead th {
    font-size: 0.72rem !important;
    padding: 10px 6px !important;
    white-space: normal !important; /* Allow headers to wrap if needed */
    word-wrap: break-word !important;
}

.dl-table tbody td {
    font-size: 0.8rem !important;
    padding: 8px 6px !important;
    white-space: normal !important;
    word-wrap: break-word !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}
"""

idx = src.rfind("</style>")
if idx > 0:
    if "/* ===== STRICT FIT WITHIN SCREEN ===== */" not in src:
        src = src[:idx] + add + src[idx:]
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(src)
        print("Strict width fit applied.")

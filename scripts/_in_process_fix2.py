"""Fix layout, search box, and dark borders on in_process.html."""
import io, os
path = os.path.join("modules", "lab", "templates", "lab", "in_process.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== FIX OVERRIDES ===== */

/* 1. Stop header text from wrapping weirdly */
.tip-header {
    display: flex !important;
    justify-content: flex-start !important;
    align-items: center !important;
    gap: 20px !important;
    border: 2px solid #212529 !important; /* Dark border */
}
.tip-header .tip-sub {
    margin-top: 0 !important;
    padding-top: 4px !important;
    flex: 1 !important;
    text-align: right !important;
}

/* 2. Fix the search box layout and remove weird pseudo-element */
.tip-filter {
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    padding: 14px 16px !important;
    border: 2px solid #212529 !important; /* Dark border */
}
.tip-filter::before {
    content: none !important; /* Remove the weird absolute label */
}
/* Add a label back nicely inside the flexbox */
.tip-filter label, .tip-filter span {
    display: none !important;
}
.tip-filter::before {
    content: "SEARCH" !important;
    position: static !important;
    background: transparent !important;
    color: #212529 !important;
    font-weight: 800 !important;
    font-size: 0.85rem !important;
    margin-right: 10px !important;
    padding: 0 !important;
}
.tip-filter input {
    flex: 1 !important;
    max-width: 400px !important;
    border: 1px solid #212529 !important;
    border-radius: 4px !important;
    height: 38px !important;
    padding: 0 12px !important;
    background: #fff !important;
}
.tip-filter input:focus {
    border-color: #0d6efd !important;
    box-shadow: none !important;
}

/* 3. Dark borders on heading band */
.tip-band {
    border: 2px solid #212529 !important;
    border-radius: 6px !important;
    padding: 12px 16px !important;
}

/* 4. Dark borders around the card and table headers */
.tip-card {
    border: 2px solid #212529 !important;
    border-radius: 6px !important;
    overflow: hidden !important;
}
.tip-table {
    border: none !important;
}
.tip-table thead th {
    border: 1px solid #212529 !important;
    border-bottom: 2px solid #212529 !important;
    text-align: center !important;
    font-size: 0.85rem !important;
    padding: 12px 8px !important;
    background: #1a3d7c !important;
}
.tip-table thead th:last-child {
    border-right: 1px solid #212529 !important;
}
/* Dark borders on body cells */
.tip-table tbody td {
    border-bottom: 1px solid #ced4da !important;
    border-right: 1px solid #ced4da !important;
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
    if "/* ===== FIX OVERRIDES ===== */" not in src:
        src = src[:idx] + add + src[idx:]
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(src)
        print("Layout and borders fixed.")
    else:
        print("Already applied.")
else:
    print("</style> not found")

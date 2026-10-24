"""Fix visible dark borders, restore header/filter visibility."""
import io, os
path = os.path.join("modules", "lab", "templates", "lab", "in_process.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== BORDER VISIBILITY FIX ===== */

/* 1. Remove the 40px top padding that hides the filter */
.tip-filter {
    padding: 14px 16px !important;
    padding-top: 14px !important;
    margin-top: 16px !important;
}

/* 2. Make the outer card border thick and impossible to miss */
.tip-card {
    border: 3px solid #212529 !important;
    border-radius: 8px !important;
    overflow: visible !important; /* Stop clipping */
    box-shadow: 0 0 0 1px #212529 !important; /* Double reinforcement */
    margin-top: 16px !important;
}

/* 3. Table borders must sit inside the dark card border */
.tip-table {
    border: none !important;
    border-radius: 0 !important;
    margin-bottom: 0 !important;
}
.tip-table thead th {
    border: 1px solid #343a40 !important;
    border-bottom: 2px solid #212529 !important;
    padding: 12px 8px !important;
}
.tip-table tbody td {
    border: 1px solid #dee2e6 !important;
    border-top: none !important;
    padding: 10px 12px !important;
}
/* Ensure the outer table doesn't have a redundant border overlapping the card */
.tip-table {
    outline: none !important;
}

/* 4. Ensure header visible */
.tip-header {
    margin-top: 16px !important;
}
"""

idx = src.rfind("</style>")
if idx > 0:
    if "/* ===== BORDER VISIBILITY FIX ===== */" not in src:
        src = src[:idx] + add + src[idx:]
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(src)
        print("Borders and visibility fixed.")
    else:
        print("Already applied.")
else:
    print("</style> not found.")

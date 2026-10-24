"""Fix missing buttons and finalize Reports theme for receiving.html."""
import io, os
path = os.path.join("modules", "lab", "templates", "lab", "receiving.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== FIX BUTTONS AND TABLE HEADERS ===== */
/* Restore the green "Mark Received" buttons */
.sr-table .btn, .sr-table button {
    display: inline-block !important;
    padding: 6px 14px !important;
    font-size: 0.8rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.03em !important;
    color: #fff !important;
    background: #198754 !important;
    border: 1px solid #146c43 !important;
    border-radius: 4px !important;
    text-decoration: none !important;
    cursor: pointer !important;
    box-shadow: none !important;
}
.sr-table .btn:hover, .sr-table button:hover {
    background: #146c43 !important;
    color: #fff !important;
}

/* Restore the red/amber/blue badges */
.sr-table .badge-green, .sr-table .badge-red, .sr-table .badge-amber, .sr-table .badge-grey {
    display: inline-block !important;
    padding: 4px 8px !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    border-radius: 4px !important;
}
.sr-table .badge-green { background: #d1e7dd !important; color: #0f5132 !important; }
.sr-table .badge-amber { background: #fff3cd !important; color: #664d03 !important; }
.sr-table .badge-red   { background: #f8d7da !important; color: #842029 !important; }
.sr-table .badge-grey  { background: #e2e3e5 !important; color: #383d41 !important; }

/* Force table headers to look exactly like reports (flat blue) */
.sr-table thead th {
    background: #1a3d7c !important;
    border: 1px solid #212529 !important;
    border-bottom: 2px solid #212529 !important;
}
/* Force the outer table and card to be dark */
.sr-card, .sr-table {
    border: 2px solid #212529 !important;
}
/* Fix the data cell borders to match Reports (light gray) */
.sr-table tbody td {
    border-bottom: 1px solid #dee2e6 !important;
    border-right: 1px solid #dee2e6 !important;
}
.sr-table tbody td:last-child {
    border-right: none !important;
}
"""

idx = src.rfind("</style>")
if idx > 0:
    if "/* ===== FIX BUTTONS AND TABLE HEADERS ===== */" not in src:
        src = src[:idx] + add + src[idx:]
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(src)
        print("Buttons, badges, and table borders fixed.")
    else:
        print("Already applied.")

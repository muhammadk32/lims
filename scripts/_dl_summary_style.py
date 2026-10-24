"""Style .dl-summary fields with individual colors + dark borders."""
import io, os
path = os.path.join("modules", "orders", "templates", "orders", "list.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== FOOTER SUMMARY: BORDERS + COLORED FIELDS ===== */
.dl-summary {
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 0 !important; /* no gaps — cells touch to form a grid */
    margin-top: 0 !important;
    border: 2px solid #212529 !important;
    border-radius: 0 0 8px 8px !important;
    overflow: hidden !important;
    background: #fff !important;
}
.dl-summary .stat {
    flex: 1 1 0 !important;
    min-width: 140px !important;
    border-right: 1px solid #212529 !important;
    padding: 12px 16px !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 4px !important;
    background: #f8f9fa !important;
}
.dl-summary .stat:last-child {
    border-right: none !important;
}
.dl-summary .stat .label {
    font-size: 0.72rem !important;
    font-weight: 800 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    color: #6c757d !important;
}
.dl-summary .stat .value {
    font-size: 1rem !important;
    font-weight: 800 !important;
    color: #212529 !important;
    font-family: Consolas, Monaco, monospace !important;
}

/* Individual field colors */
.dl-summary .stat:nth-child(1) { background: #eef4ff !important; } /* Total Amount - blue */
.dl-summary .stat:nth-child(2) { background: #fef2f2 !important; } /* Discounted - red */
.dl-summary .stat:nth-child(3) { background: #f0fdf4 !important; } /* Net Amount - green */
.dl-summary .stat:nth-child(4) { background: #f8f9fa !important; } /* Received - grey */
.dl-summary .stat:nth-child(5) { background: #fef2f2 !important; } /* Due Amount - red */
.dl-summary .stat:nth-child(6) { background: #fff8e1 !important; } /* No. of Cases - amber */

/* Match value colors to their fields */
.dl-summary .stat:nth-child(1) .value { color: #1a3d7c !important; }
.dl-summary .stat:nth-child(2) .value { color: #b02a37 !important; }
.dl-summary .stat:nth-child(3) .value { color: #146c43 !important; }
.dl-summary .stat:nth-child(5) .value { color: #b02a37 !important; }
.dl-summary .stat:nth-child(6) .value { color: #664d03 !important; }
"""

idx = src.rfind("</style>")
if idx > 0:
    if "/* ===== FOOTER SUMMARY: BORDERS + COLORED FIELDS ===== */" not in src:
        src = src[:idx] + add + src[idx:]
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(src)
        print("Footer summary styled.")
    else:
        print("Already applied.")

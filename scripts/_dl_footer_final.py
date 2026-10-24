"""Make footer box white with dark borders and colored inner shading."""
import io, os
path = os.path.join("modules", "orders", "templates", "orders", "list.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== FIX FOOTER SUMMARY COLORS ===== */
.dl-summary {
    display: flex !important;
    flex-wrap: wrap !important;
    margin-top: 16px !important;
    border: 2px solid #212529 !important; /* Dark border around whole footer */
    border-radius: 8px !important;
    background: #fff !important; /* Outer box is white */
    overflow: hidden !important;
}

.dl-summary .stat {
    flex: 1 1 0 !important;
    min-width: 140px !important;
    border-right: 1px solid #212529 !important; /* Dark divider between cells */
    padding: 12px 16px !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 4px !important;
    /* NO background color here, let the shades below apply */
}
.dl-summary .stat:last-child {
    border-right: none !important;
}

/* Individual pastel shades */
.dl-summary .stat:nth-child(1) { background: #f0f7ff !important; }
.dl-summary .stat:nth-child(2) { background: #fef2f2 !important; }
.dl-summary .stat:nth-child(3) { background: #f0fdf4 !important; }
.dl-summary .stat:nth-child(4) { background: #f8f9fa !important; }
.dl-summary .stat:nth-child(5) { background: #fef2f2 !important; }
.dl-summary .stat:nth-child(6) { background: #fff8e1 !important; }

/* Text colors */
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
    font-family: Consolas, Monaco, monospace !important;
    color: #212529 !important;
}

/* Value colors matching themes */
.dl-summary .stat:nth-child(1) .value { color: #1a3d7c !important; }
.dl-summary .stat:nth-child(2) .value { color: #b02a37 !important; }
.dl-summary .stat:nth-child(3) .value { color: #146c43 !important; }
.dl-summary .stat:nth-child(5) .value { color: #b02a37 !important; }
.dl-summary .stat:nth-child(6) .value { color: #664d03 !important; }
"""

# Remove the old broken block
if "/* ===== FOOTER SUMMARY: BORDERS + COLORED FIELDS ===== */" in src:
    start = src.find("/* ===== FOOTER SUMMARY: BORDERS + COLORED FIELDS ===== */")
    end = src.find("</style>", start)
    src = src[:start] + add + src[end:]
else:
    idx = src.rfind("</style>")
    src = src[:idx] + add + src[idx:]

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("Footer styled with clean dark borders and pastel shades.")

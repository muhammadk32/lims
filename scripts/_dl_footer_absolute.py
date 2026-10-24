"""Force footer cells to fill with color perfectly."""
import io, os
path = os.path.join("modules", "orders", "templates", "orders", "list.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== ABSOLUTE FOOTER SHADING FIX ===== */
.dl-summary {
    display: grid !important;
    grid-template-columns: repeat(6, 1fr) !important;
    gap: 0 !important; /* No gaps, cells touch */
    margin-top: 16px !important;
    border: 2px solid #212529 !important;
    border-radius: 8px !important;
    background: #fff !important;
    overflow: hidden !important;
    padding: 0 !important;
}

.dl-summary .stat {
    border-right: 1px solid #212529 !important;
    padding: 16px !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 6px !important;
    box-sizing: border-box !important;
}
.dl-summary .stat:last-child {
    border-right: none !important;
}

/* Hardcode the background colors directly to the stat boxes */
.dl-summary .stat:nth-child(1) { background-color: #f0f7ff !important; } /* Light Blue */
.dl-summary .stat:nth-child(2) { background-color: #fef2f2 !important; } /* Light Red */
.dl-summary .stat:nth-child(3) { background-color: #f0fdf4 !important; } /* Light Green */
.dl-summary .stat:nth-child(4) { background-color: #f8f9fa !important; } /* Light Grey */
.dl-summary .stat:nth-child(5) { background-color: #fef2f2 !important; } /* Light Red */
.dl-summary .stat:nth-child(6) { background-color: #fff8e1 !important; } /* Light Amber */

/* Ensure text sits on top */
.dl-summary .stat .label {
    font-size: 0.72rem !important;
    font-weight: 800 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    color: #6c757d !important;
    position: relative !important;
    z-index: 2 !important;
}
.dl-summary .stat .value {
    font-size: 1rem !important;
    font-weight: 800 !important;
    font-family: Consolas, Monaco, monospace !important;
    position: relative !important;
    z-index: 2 !important;
}

/* Value colors */
.dl-summary .stat:nth-child(1) .value { color: #1a3d7c !important; }
.dl-summary .stat:nth-child(2) .value { color: #b02a37 !important; }
.dl-summary .stat:nth-child(3) .value { color: #146c43 !important; }
.dl-summary .stat:nth-child(5) .value { color: #b02a37 !important; }
.dl-summary .stat:nth-child(6) .value { color: #664d03 !important; }
"""

if "/* ===== ABSOLUTE FOOTER SHADING FIX ===== */" not in src:
    idx = src.rfind("</style>")
    src = src[:idx] + add + src[idx:]
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("Footer shading fixed.")

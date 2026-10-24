"""Apply exact gradient table header from screenshot to receiving.html."""
import io, os
path = os.path.join("modules", "lab", "templates", "lab", "receiving.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== EXACT GRADIENT HEADER MATCH ===== */
.sr-table thead th {
    /* Gradient mimicking the screenshot */
    background: linear-gradient(180deg, #0d6efd 0%, #1a3d7c 100%) !important;
    color: #ffffff !important;
    font-family: 'Segoe UI', Arial, sans-serif !important;
    font-size: 0.85rem !important; /* Slightly larger */
    font-weight: 800 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
    padding: 14px 12px !important;
    text-align: center !important;
    vertical-align: middle !important;
    
    /* Thin subtle separator instead of harsh black */
    border-right: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-bottom: none !important; 
}
.sr-table thead th:last-child {
    border-right: none !important;
}

/* Keep the outer table box dark */
.sr-card, .sr-table {
    border: 2px solid #212529 !important;
}
"""

idx = src.rfind("</style>")
if idx > 0:
    if "/* ===== EXACT GRADIENT HEADER MATCH ===== */" not in src:
        src = src[:idx] + add + src[idx:]
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(src)
        print("Gradient header applied.")
    else:
        print("Already applied.")

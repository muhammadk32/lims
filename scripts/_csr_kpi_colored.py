"""Make KPI boxes center-aligned and multi-colored."""
import io, os
path = os.path.join("modules", "billing", "templates", "billing", "report.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== KPI COLORED & CENTERED FIX ===== */
.csr-kpi { border: none !important; }
.csr-kpi td { 
    border: none !important; 
    padding: 4px !important; 
}

/* Individual Box Styling */
.csr-kpi td:nth-child(1) { 
    background: #f0f7ff !important; 
    border: 1px solid #b6d4fe !important; 
}
.csr-kpi td:nth-child(2) { 
    background: #f0fdf4 !important; 
    border: 1px solid #a3cfbb !important; 
}
.csr-kpi td:nth-child(3) { 
    background: #fef2f2 !important; 
    border: 1px solid #f1aeb5 !important; 
}
.csr-kpi td:nth-child(4) { 
    background: #f8f9fa !important; 
    border: 1px solid #dee2e6 !important; 
}

/* Center alignment and typography */
.csr-kpi-label {
    display: block !important;
    text-align: center !important;
    font-size: 0.8rem !important;
    color: #495057 !important;
    font-weight: 700 !important;
    margin-bottom: 6px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}
.csr-kpi-value {
    display: block !important;
    text-align: center !important;
    font-size: 1.6rem !important;
    font-weight: 800 !important;
    line-height: 1.2 !important;
    color: #1a3d7c !important; /* Default color */
}

/* Override value colors */
.csr-kpi td:nth-child(2) .csr-kpi-value { color: #198754 !important; }
.csr-kpi td:nth-child(3) .csr-kpi-value { color: #dc3545 !important; }
.csr-kpi td:nth-child(4) .csr-kpi-value { color: #495057 !important; }
"""

idx = src.rfind("</style>")
if idx > 0:
    if "/* ===== KPI COLORED & CENTERED FIX ===== */" in src:
        start = src.find("/* ===== KPI COLORED & CENTERED FIX ===== */")
        src = src[:start] + add + src[idx:]
    else:
        src = src[:idx] + add + src[idx:]

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("KPI colors and centering applied.")

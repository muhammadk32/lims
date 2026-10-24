"""Remove broken generic CSS and apply strict, centered KPI + header styles."""
import io, os
path = os.path.join("modules", "billing", "templates", "billing", "report.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

# 1. Remove the broken polish block
if "/* ===== Cash Summary Report polish ===== */" in src:
    start = src.find("/* ===== Cash Summary Report polish ===== */")
    end = src.find("</style>", start)
    if end != -1:
        src = src[:start] + src[end:]

# 2. Append strict CSS at the end of the <style> block
add = """
/* ===== STRICT ALIGNMENT FIX ===== */
.csr-kpi td {
    text-align: center !important;
    vertical-align: middle !important;
    padding: 16px 12px !important;
}
.csr-kpi-label {
    display: block !important;
    font-size: 0.75rem !important;
    color: #6c757d !important;
    font-weight: 700 !important;
    margin-bottom: 6px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}
.csr-kpi-value {
    display: block !important;
    font-size: 1.4rem !important;
    font-weight: 800 !important;
    line-height: 1.1 !important;
}
.csr-table thead th {
    text-align: center !important;
    vertical-align: middle !important;
    font-size: 0.85rem !important;
    padding: 12px 8px !important;
    background: #1a3d7c !important;
    color: #fff !important;
    letter-spacing: 0.05em !important;
    border: 1px solid #343a40 !important;
}
"""

idx = src.rfind("</style>")
if idx > 0:
    src = src[:idx] + add + src[idx:]

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("Cleaned and applied strict alignment.")

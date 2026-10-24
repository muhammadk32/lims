"""Fix KPI strip: readable labels, larger font, left aligned."""
import io, os
path = os.path.join("modules", "billing", "templates", "billing", "report.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== KPI PROFESSIONAL FIX ===== */
.csr-kpi td {
    text-align: left !important;
    vertical-align: middle !important;
    padding: 16px 20px !important;
}
.csr-kpi-label {
    display: block !important;
    font-size: 0.9rem !important;
    color: #495057 !important;
    font-weight: 600 !important;
    margin-bottom: 8px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}
.csr-kpi-value {
    display: block !important;
    font-size: 1.6rem !important;
    font-weight: 800 !important;
    line-height: 1.1 !important;
}
"""

idx = src.rfind("</style>")
if idx > 0:
    # Remove previous broken strict block if it exists
    if "/* ===== STRICT ALIGNMENT FIX ===== */" in src:
        start = src.find("/* ===== STRICT ALIGNMENT FIX ===== */")
        src = src[:start] + add + src[idx:]
    else:
        src = src[:idx] + add + src[idx:]

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("KPI styling fixed.")

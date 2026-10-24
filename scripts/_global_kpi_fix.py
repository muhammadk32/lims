"""Inject global KPI center/font fixes into base.html."""
import io, os
path = os.path.join("templates", "base.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

css = """
<style>
/* ===== GLOBAL REPORT KPI FIX ===== */
/* Target the KPI tables/rows across all report pages */
.app-content .container table:not(.table-data):not([class*="report"]):has(td[class*="kpi"]),
.app-content .container .row:has([class*="kpi"]),
.app-content .container .row:has([class*="stat"]),
.app-content .container div[class*="summary"] > div {
    text-align: center !important;
}
/* Force any stat boxes / kpi cells to center */
[class*="kpi-"], [class*="stat-"] {
    text-align: center !important;
    display: block !important;
}
[class*="kpi-label"], [class*="kpi-label"] span, [class*="stat-label"],
.app-content .container td small, .app-content .container td .label {
    display: block !important;
    text-align: center !important;
    font-size: 0.85rem !important;
    font-weight: 700 !important;
    color: #6c757d !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    margin-bottom: 6px !important;
}
[class*="kpi-value"], [class*="stat-value"],
.app-content .container td strong, .app-content .container td .value {
    display: block !important;
    text-align: center !important;
    font-size: 1.5rem !important;
    font-weight: 800 !important;
    line-height: 1.2 !important;
}
/* Add a bit of padding to the KPI cells */
.app-content .container table td:has([class*="kpi-label"]),
.app-content .container table td:has([class*="stat-label"]) {
    padding: 12px 10px !important;
    vertical-align: middle !important;
}
</style>
"""

if "GLOBAL REPORT KPI FIX" not in src:
    idx = src.rfind("</head>")
    if idx > 0:
        src = src[:idx] + css + src[idx:]
    else:
        src = src.replace("</body>", css + "</body>", 1)
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("Global KPI CSS injected into base.html")
else:
    print("Already applied")

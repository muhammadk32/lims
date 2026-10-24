"""Cash Summary report: fix KPI strip + bordered cards."""
import io, os, re
path = os.path.join("modules", "billing", "templates", "billing", "report.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== Cash Summary Report polish ===== */
.app-content .container h1, .app-content .container h2, .app-content .container h3 {
  color: #1a3d7c !important;
  font-weight: 800 !important;
  letter-spacing: 0.02em !important;
}
/* KPI cells */
.app-content .container .row .col,
.app-content .container .card,
.app-content .container [class*="stat"],
.app-content .container [class*="kpi"],
.app-content .container [class*="summary"] > div {
  border: 2px solid #212529 !important;
  border-radius: 10px !important;
  background: #fff !important;
  padding: 14px 16px !important;
  text-align: center !important;
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  justify-content: center !important;
}
/* KPI labels: small, muted, uppercase */
.app-content .container .row .col small,
.app-content .container .row .col .label,
.app-content .container [class*="stat"] small,
.app-content .container [class*="kpi"] small {
  font-size: 0.72rem !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.05em !important;
  color: #6c757d !important;
  margin-bottom: 6px !important;
  display: block !important;
}
/* KPI values: big bold */
.app-content .container .row .col h4,
.app-content .container .row .col h3,
.app-content .container .row .col .value,
.app-content .container .row .col strong,
.app-content .container [class*="stat"] strong,
.app-content .container [class*="kpi"] strong {
  font-size: 1.4rem !important;
  font-weight: 800 !important;
  color: #1a3d7c !important;
  margin: 0 !important;
  line-height: 1.1 !important;
}
/* Print/Excel/Close buttons */
.app-content .container .btn {
  border-radius: 8px !important;
  font-weight: 700 !important;
  padding: 8px 18px !important;
  border-width: 2px !important;
}
.app-content .container .btn-primary {
  background: linear-gradient(135deg, #1a3d7c 0%, #0d6efd 100%) !important;
  border-color: #1a3d7c !important;
  color: #fff !important;
}
.app-content .container .btn-success {
  background: linear-gradient(135deg, #198754 0%, #20c997 100%) !important;
  border-color: #198754 !important;
  color: #fff !important;
}
.app-content .container .btn-secondary {
  background: #fff !important;
  border-color: #495057 !important;
  color: #495057 !important;
}
/* Table header/body */
.app-content .container table thead th {
  background: linear-gradient(135deg, #1a3d7c 0%, #0d6efd 100%) !important;
  color: #fff !important;
  font-weight: 800 !important;
  font-size: 0.82rem !important;
  padding: 12px 12px !important;
  text-transform: uppercase !important;
  letter-spacing: 0.04em !important;
}
.app-content .container table tbody td {
  font-size: 0.92rem !important;
  padding: 10px 12px !important;
  border-bottom: 1px solid #dee2e6 !important;
}
.app-content .container table tbody tr:nth-child(even) td {
  background: #f7f9fc !important;
}
.app-content .container table tbody tr:hover td {
  background: #eaf2ff !important;
}
"""

idx = src.rfind("</style>")
if "Cash Summary Report polish" not in src:
    if idx > 0:
        src = src[:idx] + add + src[idx:]
    else:
        anchor = "{% block content %}"
        if anchor in src:
            src = src.replace(anchor, anchor + "\n<style>" + add + "</style>", 1)
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("report styles added")
else:
    print("already present")

"""Fix KPI strip using actual csr-* classes."""
import io, os
path = os.path.join("modules", "billing", "templates", "billing", "report.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== KPI cells — csr-* classes ===== */
.csr-kpi {
  width: 100% !important;
  border-collapse: separate !important;
  border-spacing: 8px !important;
  margin-bottom: 16px !important;
}
.csr-kpi td {
  border: 2px solid #212529 !important;
  border-radius: 10px !important;
  background: #fff !important;
  padding: 14px 16px !important;
  text-align: center !important;
  vertical-align: middle !important;
  width: 25% !important;
}
.csr-kpi-label {
  font-size: 0.78rem !important;
  font-weight: 800 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.06em !important;
  color: #495057 !important;
  margin-bottom: 8px !important;
  display: block !important;
  line-height: 1.2 !important;
}
.csr-kpi-value {
  font-size: 1.5rem !important;
  font-weight: 900 !important;
  color: #1a3d7c !important;
  line-height: 1.1 !important;
  display: block !important;
}
.csr-kpi-value.csr-success { color: #198754 !important; }
.csr-kpi-value.csr-danger  { color: #dc3545 !important; }
"""

idx = src.rfind("</style>")
if ".csr-kpi-label {" not in src:
    src = src[:idx] + add + src[idx:]
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("csr-kpi styles added")

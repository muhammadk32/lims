"""Override tip-* styles to match Reports (Cash Summary) theme."""
import io, os
path = os.path.join("modules", "lab", "templates", "lab", "in_process.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== Match Reports (Cash Summary) theme ===== */
.tip-page { padding: 16px 24px 40px !important; }

.tip-header {
  background: linear-gradient(135deg, #1a3d7c 0%, #0d6efd 100%) !important;
  border: none !important;
  border-radius: 10px !important;
  padding: 16px 20px !important;
  margin-bottom: 16px !important;
  color: #fff !important;
  display: flex !important;
  justify-content: space-between !important;
  align-items: center !important;
}
.tip-header .tip-title,
.tip-header .tip-title i { color: #fff !important; }
.tip-header .tip-title { font-size: 1.25rem !important; text-transform: uppercase !important; letter-spacing: 0.02em !important; }
.tip-header .tip-sub { color: #dbeafe !important; font-size: 0.85rem !important; font-family: Consolas, monospace !important; }

.tip-filter {
  background: #fff !important;
  border: 1px solid #dee2e6 !important;
  border-radius: 8px !important;
  padding: 14px 16px !important;
  margin-bottom: 16px !important;
}
.tip-filter::before {
  content: "\\f4fe  SEARCH" !important;
  font-family: 'bootstrap-icons', 'Segoe UI', Arial, sans-serif !important;
  background: #f0f7ff !important;
  color: #1a3d7c !important;
  font-weight: 700 !important;
  font-size: 0.78rem !important;
  letter-spacing: 0.06em !important;
  padding: 6px 14px !important;
}
.tip-filter input {
  border: 1px solid #ced4da !important;
  background: #fff !important;
  color: #212529 !important;
  border-radius: 6px !important;
  height: 38px !important;
}
.tip-filter input:focus {
  border-color: #0d6efd !important;
  box-shadow: 0 0 0 3px rgba(13,110,253,0.15) !important;
}

.tip-btn {
  border-radius: 6px !important;
  font-weight: 700 !important;
  border-width: 1px !important;
}
.tip-btn-primary, .tip-btn-search {
  background: linear-gradient(135deg, #1a3d7c 0%, #0d6efd 100%) !important;
  border-color: #1a3d7c !important;
  color: #fff !important;
}

.tip-band {
  background: #fff8e1 !important;
  border: 1px solid #ffe69c !important;
  color: #664d03 !important;
  font-weight: 700 !important;
  padding: 10px 16px !important;
  border-radius: 8px !important;
  font-size: 0.85rem !important;
  text-transform: uppercase !important;
  letter-spacing: 0.05em !important;
  margin-bottom: 0 !important;
}

.tip-card {
  background: #fff !important;
  border: 1px solid #dee2e6 !important;
  border-radius: 8px !important;
  overflow: hidden !important;
}

.tip-table {
  border: none !important;
  border-radius: 0 !important;
  border-collapse: collapse !important;
}
.tip-table thead th {
  background: #1a3d7c !important;
  color: #fff !important;
  font-size: 0.82rem !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.04em !important;
  padding: 12px 12px !important;
  text-align: center !important;
  border: 1px solid #343a40 !important;
  border-top: none !important;
}
.tip-table tbody td {
  padding: 10px 12px !important;
  border-bottom: 1px solid #dee2e6 !important;
  border-right: 1px solid #f1f3f5 !important;
  font-size: 0.9rem !important;
  background: #fff !important;
}
.tip-table tbody td:last-child { border-right: none !important; }
.tip-table tbody tr:nth-child(even) td { background: #fbfcfd !important; }
.tip-table tbody tr:hover td { background: #eaf2ff !important; }
.tip-table code {
  background: #eef4ff !important;
  color: #1a3d7c !important;
  font-weight: 600 !important;
}
"""

idx = src.rfind("</style>")
if idx > 0:
    if "Match Reports (Cash Summary) theme" not in src:
        src = src[:idx] + add + src[idx:]
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(src)
        print("in_process.html styled to match Reports theme")
    else:
        print("Already applied")
else:
    print("</style> not found")

"""Apply the Test In Process theme to receiving.html (.sr-* classes)."""
import io, os
path = os.path.join("modules", "lab", "templates", "lab", "receiving.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

# Remove any previously applied failed block
if "/* ===== MATCH TEST IN PROCESS THEME ===== */" in src:
    start = src.find("/* ===== MATCH TEST IN PROCESS THEME ===== */")
    end = src.find("</style>", start)
    src = src[:start] + src[end:]

add = """
/* ===== SR THEME MATCH ===== */
.sr-page { padding: 16px 24px 40px !important; }

.sr-header {
  background: linear-gradient(135deg, #1a3d7c 0%, #0d6efd 100%) !important;
  border: 2px solid #212529 !important;
  border-radius: 10px !important;
  padding: 16px 20px !important;
  margin-bottom: 16px !important;
  color: #fff !important;
  display: flex !important;
  justify-content: space-between !important;
  align-items: center !important;
}
.sr-header .sr-title, .sr-header .sr-title i { color: #fff !important; font-size: 1.25rem !important; text-transform: uppercase !important; }
.sr-header .sr-sub { color: #dbeafe !important; font-family: Consolas, monospace !important; margin: 0 !important; }

.sr-filter {
  display: flex !important;
  align-items: center !important;
  gap: 10px !important;
  padding: 14px 16px !important;
  padding-top: 14px !important;
  background: #fff !important;
  border: 2px solid #212529 !important;
  border-radius: 8px !important;
  margin-bottom: 16px !important;
}
.sr-filter::before {
  content: "SEARCH" !important;
  position: static !important;
  background: transparent !important;
  color: #212529 !important;
  font-weight: 800 !important;
  font-size: 0.85rem !important;
  margin-right: 10px !important;
  padding: 0 !important;
}
.sr-filter input {
  flex: 1 !important;
  max-width: 400px !important;
  border: 1px solid #212529 !important;
  border-radius: 4px !important;
  height: 38px !important;
  padding: 0 12px !important;
  background: #fff !important;
}
.sr-filter .sr-btn, .sr-filter .sr-btn-primary {
  background: #198754 !important;
  border: 1px solid #198754 !important;
  color: #fff !important;
  font-weight: 700 !important;
  height: 38px !important;
  padding: 0 20px !important;
  border-radius: 4px !important;
}

.sr-band {
  background: #fff8e1 !important;
  border: 2px solid #212529 !important;
  color: #664d03 !important;
  font-weight: 700 !important;
  padding: 12px 16px !important;
  border-radius: 6px !important;
  font-size: 0.85rem !important;
  text-transform: uppercase !important;
  letter-spacing: 0.05em !important;
  margin-bottom: 16px !important;
}

.sr-card {
  border: 2px solid #212529 !important;
  border-radius: 6px !important;
  overflow: hidden !important;
  background: #fff !important;
  padding: 0 !important;
}
.sr-table {
  border-collapse: collapse !important;
  width: 100% !important;
  margin: 0 !important;
  border: 2px solid #212529 !important;
}
.sr-table thead th {
  border: 1px solid #212529 !important;
  background: #1a3d7c !important;
  color: #fff !important;
  text-align: center !important;
  padding: 12px 8px !important;
  font-size: 0.85rem !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
}
.sr-table tbody td {
  border: 1px solid #212529 !important;
  padding: 10px 12px !important;
  background: #fff !important;
}
.sr-table tbody tr:hover td { background: #eaf2ff !important; }
"""

idx = src.rfind("</style>")
if idx > 0:
    src = src[:idx] + add + src[idx:]
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("Theme applied to receiving.html")
else:
    print("</style> not found.")

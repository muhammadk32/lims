"""Apply polished theme to Daily Ledger (dl-*)."""
import io, os
path = os.path.join("modules", "orders", "templates", "orders", "list.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== POLISHED THEME ===== */
.dl-page {
  max-width: 100% !important;
  padding: 16px 32px 40px !important;
  font-family: 'Segoe UI', Arial, sans-serif !important;
  font-size: 0.82rem !important;
  color: #212529 !important;
}

/* Header */
.dl-header {
  display: flex !important;
  justify-content: space-between !important;
  align-items: flex-end !important;
  background: linear-gradient(135deg, #1a3d7c 0%, #0d6efd 100%) !important;
  border: 2px solid #212529 !important;
  border-radius: 10px !important;
  padding: 16px 20px !important;
  margin-bottom: 16px !important;
  color: #fff !important;
  flex-wrap: wrap !important;
  gap: 8px !important;
}
.dl-title {
  font-size: 1.25rem !important;
  font-weight: 700 !important;
  margin: 0 !important;
  letter-spacing: 0.02em !important;
  text-transform: uppercase !important;
  color: #fff !important;
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
}
.dl-title i { color: #fff !important; }
.dl-subtitle {
  font-size: 0.85rem !important;
  color: #dbeafe !important;
  font-family: Consolas, Monaco, monospace !important;
  margin-top: 2px !important;
}
.dl-count {
  font-size: 0.85rem !important;
  color: #dbeafe !important;
  font-family: Consolas, Monaco, monospace !important;
}

/* Filter box */
.dl-filter {
  background: #fff !important;
  border: 2px solid #212529 !important;
  border-radius: 8px !important;
  padding: 14px 16px !important;
  margin-bottom: 16px !important;
  position: static !important;
}
.dl-filter::before { content: none !important; display: none !important; }
.dl-filter-row {
  display: grid !important;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)) !important;
  gap: 12px !important;
  align-items: end !important;
}
.dl-field { display: flex !important; flex-direction: column !important; gap: 4px !important; }
.dl-field label {
  font-size: 0.72rem !important;
  font-weight: 700 !important;
  letter-spacing: 0.05em !important;
  text-transform: uppercase !important;
  color: #6c757d !important;
}
.dl-filter input, .dl-filter select {
  height: 38px !important;
  padding: 0 12px !important;
  border: 1px solid #ced4da !important;
  border-radius: 4px !important;
  background: #fff !important;
  font-size: 0.9rem !important;
  color: #212529 !important;
  width: 100% !important;
  box-sizing: border-box !important;
}
.dl-filter input:focus, .dl-filter select:focus {
  outline: none !important;
  border-color: #0d6efd !important;
  box-shadow: 0 0 0 3px rgba(13,110,253,0.15) !important;
}

/* Quick range buttons */
.dl-quick {
  display: flex !important;
  gap: 6px !important;
  flex-wrap: wrap !important;
  margin-top: 10px !important;
}
.dl-quick a, .dl-quick button {
  height: 30px !important;
  padding: 0 14px !important;
  font-size: 0.78rem !important;
  font-weight: 700 !important;
  border-radius: 20px !important;
  background: #fff !important;
  color: #212529 !important;
  border: 1px solid #ced4da !important;
  text-decoration: none !important;
  display: inline-flex !important;
  align-items: center !important;
}
.dl-quick a:hover, .dl-quick button:hover {
  background: #eaf2ff !important;
  border-color: #0d6efd !important;
  color: #1a3d7c !important;
}

/* Filter button */
.dl-filter button[type=submit], .dl-btn-filter {
  height: 38px !important;
  padding: 0 18px !important;
  font-size: 0.85rem !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
  border-radius: 4px !important;
  border: 1px solid #198754 !important;
  background: #198754 !important;
  color: #fff !important;
  cursor: pointer !important;
}

/* Yellow band */
.dl-band {
  background: #fff8e1 !important;
  border: 2px solid #212529 !important;
  color: #664d03 !important;
  font-weight: 700 !important;
  padding: 10px 16px !important;
  border-radius: 8px !important;
  font-size: 0.85rem !important;
  text-transform: uppercase !important;
  letter-spacing: 0.05em !important;
  margin-bottom: 16px !important;
}

/* Table */
.dl-card {
  border: none !important;
  overflow: visible !important;
  background: transparent !important;
  margin-bottom: 20px !important;
}
.dl-table {
  width: 100% !important;
  border-collapse: separate !important;
  border-spacing: 0 !important;
  border: 2px solid #212529 !important;
  border-radius: 8px 8px 0 0 !important;
  background: #fff !important;
  margin: 0 !important;
}
.dl-table thead th {
  background: linear-gradient(180deg, #0d6efd 0%, #1a3d7c 100%) !important;
  color: #fff !important;
  font-size: 0.85rem !important;
  font-weight: 800 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.04em !important;
  padding: 14px 12px !important;
  text-align: center !important;
  vertical-align: middle !important;
  border-right: 1px solid #212529 !important;
  border-bottom: 2px solid #212529 !important;
}
.dl-table thead th:first-child { border-top-left-radius: 8px !important; }
.dl-table thead th:last-child {
  border-top-right-radius: 8px !important;
  border-right: none !important;
}
.dl-table tbody td {
  font-size: 1rem !important;
  padding: 12px 12px !important;
  border-bottom: 1px solid #212529 !important;
  border-right: 1px solid #212529 !important;
  vertical-align: middle !important;
  color: #212529 !important;
  background: #fff !important;
}
.dl-table tbody td:last-child { border-right: none !important; }
.dl-table tbody tr:hover td { background: #eaf2ff !important; }

/* Buttons inside table (dropdown toggle) */
.dl-table .btn, .dl-table button {
  display: inline-block !important;
  padding: 4px 10px !important;
  font-size: 0.78rem !important;
  font-weight: 700 !important;
  border-radius: 4px !important;
  border: 1px solid #212529 !important;
  background: #fff !important;
  color: #212529 !important;
}

/* Empty state */
.dl-empty, .alert-info {
  background: #fff8e1 !important;
  border: 2px solid #212529 !important;
  border-radius: 8px !important;
  color: #664d03 !important;
  padding: 40px 20px !important;
  font-weight: 700 !important;
}
"""

idx = src.rfind("</style>")
if idx > 0:
    if "/* ===== POLISHED THEME ===== */" not in src:
        src = src[:idx] + add + src[idx:]
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(src)
        print("Polished theme applied to Daily Ledger.")
    else:
        print("Already applied.")
else:
    css = f"<style>\n{add}\n</style>\n"
    anchor = "{% block head %}"
    if anchor in src:
        src = src.replace(anchor, anchor + "\n" + css, 1)
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(src)
        print("Polished theme inserted.")
    else:
        print("No style block / head anchor.")

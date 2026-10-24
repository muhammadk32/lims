"""Apply polished theme to verify.html (lv-* classes)."""
import io, os
path = os.path.join("modules", "lab", "templates", "lab", "verify.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== POLISHED THEME OVERRIDE ===== */
.lv-page {
  max-width: 100% !important;
  padding: 16px 32px 40px !important;
  font-family: 'Segoe UI', Arial, sans-serif !important;
  font-size: 0.82rem !important;
  color: #212529 !important;
  display: flex !important;
  gap: 20px !important;
}
.lv-left {
  flex: 1 1 auto !important;
  min-width: 0 !important;
}

/* Header Bar */
.lv-header {
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
.lv-title {
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
.lv-title i { color: #fff !important; }
.lv-subtitle {
  font-size: 0.85rem !important;
  color: #dbeafe !important;
  font-family: Consolas, Monaco, monospace !important;
  margin-top: 2px !important;
}
.lv-count {
  font-size: 0.85rem !important;
  color: #dbeafe !important;
  font-family: Consolas, Monaco, monospace !important;
}

/* Filter Box */
.lv-filter {
  background: #fff !important;
  border: 2px solid #212529 !important;
  border-radius: 8px !important;
  padding: 14px 16px !important;
  margin-bottom: 16px !important;
  position: static !important;
}
.lv-filter::before { content: none !important; display: none !important; }
.lv-filter-row {
  display: grid !important;
  grid-template-columns: 2fr 1fr 1fr auto !important;
  gap: 12px !important;
  align-items: end !important;
}
.lv-field { display: flex !important; flex-direction: column !important; gap: 4px !important; }
.lv-field label {
  font-size: 0.72rem !important;
  font-weight: 700 !important;
  letter-spacing: 0.05em !important;
  text-transform: uppercase !important;
  color: #6c757d !important;
}
.lv-filter input, .lv-filter select {
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
.lv-filter input:focus, .lv-filter select:focus {
  outline: none !important;
  border-color: #0d6efd !important;
  box-shadow: 0 0 0 3px rgba(13,110,253,0.15) !important;
}

/* Buttons */
.lv-filter button, .lv-btn, .btn-filter {
  height: 38px !important;
  padding: 0 18px !important;
  font-size: 0.85rem !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.03em !important;
  border-radius: 4px !important;
  border: 1px solid #198754 !important;
  background: #198754 !important;
  color: #fff !important;
  cursor: pointer !important;
}
.lv-filter .btn-clear, .btn-clear {
  background: #fff !important;
  color: #212529 !important;
  border: 1px solid #212529 !important;
}

/* Table Card */
.lv-table {
  width: 100% !important;
  border-collapse: separate !important;
  border-spacing: 0 !important;
  border: 2px solid #212529 !important;
  border-radius: 8px 8px 0 0 !important;
  background: #fff !important;
  margin: 0 !important;
}
.lv-table thead th {
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
.lv-table thead th:first-child { border-top-left-radius: 8px !important; }
.lv-table thead th:last-child {
  border-top-right-radius: 8px !important;
  border-right: none !important;
}
.lv-table tbody td {
  font-size: 1rem !important;
  padding: 12px 12px !important;
  border-bottom: 1px solid #212529 !important;
  border-right: 1px solid #212529 !important;
  vertical-align: middle !important;
  color: #212529 !important;
  background: #fff !important;
}
.lv-table tbody td:last-child { border-right: none !important; }
.lv-table tbody tr:hover td { background: #eaf2ff !important; }

/* Status column shading */
.lv-table tbody td:nth-child(8) {
  background-color: #fff8e1 !important;
  font-weight: 700 !important;
}

/* Bulk bar */
.lv-bulkbar {
  background: #fff8e1 !important;
  border: 2px solid #212529 !important;
  border-radius: 8px !important;
  padding: 10px 16px !important;
  margin-bottom: 16px !important;
}

/* Empty / right panel */
.lv-right, .preview-panel {
  border: 2px solid #212529 !important;
  border-radius: 8px !important;
  background: #fff !important;
}
"""

idx = src.rfind("</style>")
if idx > 0:
    if "/* ===== POLISHED THEME OVERRIDE ===== */" not in src:
        src = src[:idx] + add + src[idx:]
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(src)
        print("Polished theme applied to verify.html")
    else:
        print("Already applied.")
else:
    # No style block: insert after {% block head %}
    css = f"<style>\n{add}\n</style>\n"
    anchor = "{% block head %}"
    if anchor in src:
        src = src.replace(anchor, anchor + "\n" + css, 1)
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(src)
        print("Polished theme inserted (new style block).")
    else:
        print("No style block / head anchor found.")

"""Copy polished SR styles to In Process page (changing sr- to tip-)."""
import io, os
path = os.path.join("modules", "lab", "templates", "lab", "in_process.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

new_css = """
<style>
/* ============================================================
   MATCHING SAMPLE RECEIVING THEME
   ============================================================ */
.tip-page {
  max-width: 100% !important;
  margin: 0 auto;
  padding: 16px 32px 40px !important;
  font-family: 'Segoe UI', Arial, sans-serif;
  font-size: 0.82rem;
  color: #212529;
}

/* Header */
.tip-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  background: linear-gradient(135deg, #1a3d7c 0%, #0d6efd 100%);
  border: none;
  border-radius: 10px;
  padding: 16px 20px;
  margin-bottom: 16px;
  color: #fff;
}
.tip-title {
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0;
  letter-spacing: 0.02em;
  text-transform: uppercase;
  color: #fff;
  display: flex;
  align-items: center;
  gap: 8px;
}
.tip-title i { color: #fff; }
.tip-sub {
  font-size: 0.85rem;
  color: #dbeafe;
  font-family: Consolas, Monaco, monospace;
  margin: 0;
}

/* Filter Box */
.tip-filter {
  display: flex;
  gap: 12px;
  align-items: center;
  background: #fff;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 14px 16px;
  margin-bottom: 16px;
}
.tip-filter::before { content: none; display: none; }
.tip-filter input {
  flex: 1;
  max-width: 400px;
  height: 38px;
  padding: 0 12px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  background: #fff;
  font-size: 0.9rem;
}
.tip-filter input:focus {
  outline: none;
  border-color: #0d6efd;
  box-shadow: 0 0 0 3px rgba(13,110,253,0.15);
}
.tip-filter .tip-btn {
  height: 38px;
  padding: 0 20px;
  background: #198754;
  border: 1px solid #198754;
  border-radius: 4px;
  color: #fff;
  font-weight: 700;
  text-transform: uppercase;
  cursor: pointer;
}

/* Band */
.tip-band {
  background: #fff8e1;
  border: 1px solid #ffe69c;
  color: #664d03;
  font-weight: 700;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 16px;
}

/* Table Card Container */
.tip-card {
  border: none !important;
  overflow: visible !important;
  background: transparent !important;
  margin-bottom: 20px;
}

/* The Table */
.tip-table {
  width: 100%;
  border-collapse: separate !important;
  border-spacing: 0 !important;
  border: 2px solid #212529 !important;
  border-radius: 8px 8px 0 0 !important;
  margin: 0;
  background: #fff;
}

/* Headers */
.tip-table thead th {
  background: linear-gradient(180deg, #0d6efd 0%, #1a3d7c 100%) !important;
  color: #ffffff !important;
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
.tip-table thead th:last-child {
  border-right: none !important;
  border-top-right-radius: 8px !important;
}
.tip-table thead th:first-child {
  border-top-left-radius: 8px !important;
}

/* Table Body Cells */
.tip-table tbody td {
  font-size: 1rem !important;
  padding: 12px 12px !important;
  border-bottom: 1px solid #212529 !important;
  border-right: 1px solid #212529 !important;
  vertical-align: middle;
  color: #212529;
}
.tip-table tbody td:last-child {
  border-right: none !important;
}
.tip-table tbody tr:hover td {
  background: #eaf2ff !important;
}

/* Status Column Shading */
.tip-table tbody td:nth-child(6) {
  background-color: #fff8e1 !important;
  color: #212529 !important;
  font-weight: 700 !important;
}

/* Buttons inside table */
.tip-table .btn, .tip-table button, .tip-btn-sm {
  display: inline-block;
  padding: 6px 14px;
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #fff;
  background: #198754;
  border: 1px solid #146c43;
  border-radius: 4px;
  text-decoration: none;
  cursor: pointer;
}
</style>
"""

start = src.find("<style>")
end = src.find("</style>") + len("</style>")
if start != -1 and end != -1:
    src = src[:start] + new_css + src[end:]
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("In Process page updated with the final polished styling.")

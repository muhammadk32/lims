"""Apply polished theme to pending results (pr-*) page."""
import io, os
path = os.path.join("modules", "results", "templates", "results", "index.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

new_css = """
<style>
/* ============================================================
   POLISHED THEME — MATCHES SAMPLE RECEIVING / REPORTS
   ============================================================ */
.pr-page {
  max-width: 100% !important;
  padding: 16px 32px 40px !important;
  font-family: 'Segoe UI', Arial, sans-serif;
  font-size: 0.82rem;
  color: #212529;
}

/* Header */
.pr-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  background: linear-gradient(135deg, #1a3d7c 0%, #0d6efd 100%);
  border: 2px solid #212529;
  border-radius: 10px;
  padding: 16px 20px;
  margin-bottom: 16px;
  color: #fff;
  flex-wrap: wrap;
  gap: 8px;
}
.pr-title {
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
.pr-title i { color: #fff; }
.pr-subtitle {
  font-size: 0.85rem;
  color: #dbeafe;
  font-family: Consolas, Monaco, monospace;
  margin-top: 2px;
}
.pr-count {
  font-size: 0.85rem;
  color: #dbeafe;
  font-family: Consolas, Monaco, monospace;
}

/* Filter box */
.pr-filter {
  display: grid;
  grid-template-columns: 2fr 1.2fr auto;
  gap: 12px;
  align-items: end;
  background: #fff;
  border: 2px solid #212529;
  border-radius: 8px;
  padding: 14px 16px;
  margin-bottom: 16px;
  position: static;
}
.pr-filter::before { content: none !important; display: none !important; }

.pr-field { display: flex; flex-direction: column; gap: 4px; }
.pr-field label {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: #6c757d;
}
.pr-filter input, .pr-filter select {
  height: 38px;
  padding: 0 12px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  background: #fff;
  font-size: 0.9rem;
  color: #212529;
  width: 100%;
  box-sizing: border-box;
}
.pr-filter input:focus, .pr-filter select:focus {
  outline: none;
  border-color: #0d6efd;
  box-shadow: 0 0 0 3px rgba(13,110,253,0.15);
}

/* Buttons */
.pr-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 38px;
  padding: 0 18px;
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  border-radius: 4px;
  border: 1px solid #198754;
  background: #198754;
  color: #fff;
  text-decoration: none;
  cursor: pointer;
}
.pr-btn-clear {
  background: #fff;
  color: #212529;
  border: 1px solid #212529;
}

/* Band */
.pr-band {
  background: #fff8e1;
  border: 2px solid #212529;
  color: #664d03;
  font-weight: 700;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 16px;
}

/* Table card */
.pr-card {
  border: none !important;
  overflow: visible !important;
  background: transparent !important;
  margin-bottom: 20px;
}
.pr-table {
  width: 100%;
  border-collapse: separate !important;
  border-spacing: 0 !important;
  border: 2px solid #212529 !important;
  border-radius: 8px 8px 0 0 !important;
  background: #fff;
  margin: 0;
}
.pr-table thead th {
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
.pr-table thead th:first-child { border-top-left-radius: 8px !important; }
.pr-table thead th:last-child {
  border-top-right-radius: 8px !important;
  border-right: none !important;
}

.pr-table tbody td {
  font-size: 1rem !important;
  padding: 12px 12px !important;
  border-bottom: 1px solid #212529 !important;
  border-right: 1px solid #212529 !important;
  vertical-align: middle !important;
  color: #212529;
}
.pr-table tbody td:last-child { border-right: none !important; }
.pr-table tbody tr:hover td { background: #eaf2ff !important; }

/* Status column shading (adjust nth-child if column count differs) */
.pr-table tbody td:nth-child(7) {
  background-color: #fff8e1 !important;
  font-weight: 700 !important;
}

/* Table buttons */
.pr-table .btn, .pr-table button, .pr-btn-sm {
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

/* Empty state */
.alert-info, .pr-empty, .text-center.py-5 {
  background: #fff8e1 !important;
  border: 2px solid #212529 !important;
  border-radius: 8px !important;
  color: #664d03 !important;
  padding: 40px 20px !important;
  font-weight: 700 !important;
}
</style>
"""

start = src.find("<style>")
end = src.find("</style>") + len("</style>")
if start != -1 and end != -1:
    src = src[:start] + new_css + src[end:]
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("Pending Results polished theme applied.")
else:
    print("Style block not found.")

"""Copy Reports (csr-*) CSS verbatim into receiving (sr-*), renaming prefix only."""
import io, os
path = os.path.join("modules", "lab", "templates", "lab", "receiving.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

new_css = """
<style>
/* ============================================================
   COPIED FROM REPORTS (Cash Summary Report)
   ============================================================ */
.sr-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 16px 24px 40px;
  font-family: 'Segoe UI', Arial, sans-serif;
  font-size: 0.82rem;
  color: #212529;
}

/* Header */
.sr-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  border-bottom: 2px solid #212529;
  padding-bottom: 8px;
  margin-bottom: 12px;
}
.sr-title {
  font-size: 1.2rem;
  font-weight: 700;
  margin: 0;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}
.sr-sub {
  font-size: 0.78rem;
  color: #6c757d;
  margin-top: 2px;
  font-family: Consolas, Monaco, monospace;
}
.sr-actions {
  display: flex;
  gap: 6px;
}
.sr-btn {
  display: inline-block;
  padding: 5px 14px;
  font-size: 0.8rem;
  font-weight: 600;
  border: 1px solid #212529;
  background: #fff;
  color: #212529;
  text-decoration: none;
  border-radius: 0;
  cursor: pointer;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}
.sr-btn:hover { background: #f1f3f5; color: #212529; }
.sr-btn-primary {
  background: #198754;
  border-color: #198754;
  color: #fff;
}
.sr-btn-primary:hover { background: #146c43; color: #fff; }

/* Filter (Reports uses a plain row of inputs — same style) */
.sr-filter {
  display: flex;
  gap: 8px;
  align-items: center;
  padding: 10px 0;
  background: #fff;
  border: none;
  border-radius: 0;
  margin-bottom: 12px;
}
.sr-filter::before {
  content: "SEARCH";
  font-size: 0.78rem;
  font-weight: 700;
  color: #6c757d;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  position: static;
  background: transparent;
  padding: 0;
  margin-right: 6px;
}
.sr-filter input {
  padding: 6px 10px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.85rem;
  height: 34px;
  max-width: 320px;
  background: #fff;
  color: #212529;
}
.sr-filter input:focus {
  outline: none;
  border-color: #0d6efd;
  box-shadow: 0 0 0 3px rgba(13,110,253,0.15);
}
.sr-filter .sr-btn {
  padding: 6px 14px;
}

/* Yellow band */
.sr-band {
  background: #fff8e1;
  border: 1px solid #ffe69c;
  color: #664d03;
  font-weight: 700;
  padding: 8px 14px;
  border-radius: 6px;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 12px;
}

/* Main table */
.sr-table {
  width: 100%;
  border-collapse: collapse;
  border: 1px solid #212529;
  font-size: 0.78rem;
}
.sr-table thead th {
  background: #1a3d7c !important;
  color: #fff !important;
  font-size: 0.82rem !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.04em !important;
  padding: 10px 12px !important;
  text-align: center !important;
  border-right: 1px solid #343a40 !important;
  white-space: nowrap !important;
  vertical-align: middle !important;
}
.sr-table thead th:last-child { border-right: none; }

.sr-table tbody td {
  padding: 5px 8px;
  border-bottom: 1px solid #dee2e6;
  border-right: 1px solid #f1f3f5;
  vertical-align: middle;
}
.sr-table tbody td:last-child { border-right: none; }
.sr-table tbody tr:nth-child(even) { background: #fbfcfd; }
.sr-table tbody tr:hover { background: #f1f3f5; }
.sr-table .muted { color: #6c757d; font-size: 0.74rem; }
.sr-table .fw-semibold { font-weight: 600; }

.sr-card {
  border: none;
  border-radius: 0;
  background: transparent;
  overflow: visible;
}
</style>
"""

start = src.find("<style>")
end = src.find("</style>") + len("</style>")
if start != -1 and end != -1:
    src = src[:start] + new_css + src[end:]
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("Copied Reports CSS into receiving.html (prefix sr-).")
else:
    print("Style block not found.")

"""Map Reports CSS exactly to receiving.html (sr-*) keeping Reports look."""
import io, os
path = os.path.join("modules", "lab", "templates", "lab", "receiving.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

new_css = """
<style>
/* ============================================================
   COPY OF REPORTS (Cash Summary) LOOK
   ============================================================ */
.sr-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 16px 24px 40px;
  font-family: 'Segoe UI', Arial, sans-serif;
  font-size: 0.82rem;
  color: #212529;
}

/* --- HEADER: Blue Gradient Bar --- */
.sr-header {
  background: linear-gradient(135deg, #1a3d7c 0%, #0d6efd 100%);
  border-radius: 10px;
  padding: 16px 20px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: none;
  color: #fff;
}
.sr-title {
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
.sr-title i { color: #fff; }
.sr-sub {
  font-size: 0.85rem;
  color: #dbeafe;
  font-family: Consolas, Monaco, monospace;
  margin: 0;
  text-align: right;
}

/* --- FILTER: White bordered box like Reports FROM/TO area --- */
.sr-filter {
  display: flex;
  gap: 12px;
  align-items: center;
  background: #fff;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 14px 16px;
  margin-bottom: 16px;
}
.sr-filter::before {
  content: "SEARCH";
  font-family: 'Segoe UI', Arial, sans-serif;
  position: static;
  background: transparent;
  color: #212529;
  font-weight: 800;
  font-size: 0.85rem;
  margin-right: 8px;
  padding: 0;
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
  flex: 1;
}
.sr-filter input:focus {
  outline: none;
  border-color: #0d6efd;
  box-shadow: 0 0 0 3px rgba(13,110,253,0.15);
}
.sr-filter .sr-btn {
  padding: 6px 16px;
  font-size: 0.85rem;
  font-weight: 600;
  border: 1px solid #198754;
  background: #198754;
  color: #fff;
  border-radius: 4px;
  cursor: pointer;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

/* --- YELLOW BAND --- */
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

/* --- TABLE CARD (outer dark border) --- */
.sr-card {
  border: 1px solid #212529;
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
}
.sr-table {
  width: 100%;
  border-collapse: collapse;
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
  padding: 8px 12px;
  border-bottom: 1px solid #dee2e6;
  border-right: 1px solid #f1f3f5;
  vertical-align: middle;
}
.sr-table tbody td:last-child { border-right: none; }
.sr-table tbody tr:nth-child(even) { background: #fbfcfd; }
.sr-table tbody tr:hover { background: #f1f3f5; }
</style>
"""

start = src.find("<style>")
end = src.find("</style>") + len("</style>")
if start != -1 and end != -1:
    src = src[:start] + new_css + src[end:]
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("Receiving page updated to match Report header/filter/table.")

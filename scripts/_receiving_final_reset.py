"""Wipe receiving.html CSS and apply exact Reports structure."""
import io, os
path = os.path.join("modules", "lab", "templates", "lab", "receiving.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

new_css = """
<style>
/* ============================================================
   EXACT MATCH TO REPORTS (Cash Summary) THEME
   ============================================================ */
.sr-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 16px 24px 40px;
  font-family: 'Segoe UI', Arial, sans-serif;
  font-size: 0.82rem;
  color: #212529;
}

/* Header: Blue Gradient, no borders, uppercase */
.sr-header {
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
}

/* Filter Box: White, light grey border, rounded */
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
.sr-filter::before { content: none; display: none; }
.sr-filter input {
  flex: 1;
  max-width: 400px;
  height: 38px;
  padding: 0 12px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  background: #fff;
  font-size: 0.9rem;
}
.sr-filter input:focus {
  outline: none;
  border-color: #0d6efd;
  box-shadow: 0 0 0 3px rgba(13,110,253,0.15);
}
.sr-filter .sr-btn {
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

/* Yellow Band: Soft, no thick dark border */
.sr-band {
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

/* Table Card: Dark border OUTSIDE only */
.sr-card {
  border: 2px solid #212529;
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
  margin-bottom: 20px;
}
.sr-table {
  width: 100%;
  border-collapse: collapse;
  margin: 0;
}

/* Table Headers: Blue background, centered */
.sr-table thead th {
  background: #1a3d7c;
  color: #fff;
  font-size: 0.82rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding: 12px 12px;
  text-align: center;
  border-bottom: 2px solid #212529; /* Divider under header */
  border-right: 1px solid #343a40;
  vertical-align: middle;
}
.sr-table thead th:last-child { border-right: none; }

/* Table Body: Light grey cell borders */
.sr-table tbody td {
  font-size: 0.9rem;
  padding: 10px 12px;
  border-bottom: 1px solid #dee2e6;
  border-right: 1px solid #f1f3f5;
  vertical-align: middle;
  color: #212529;
}
.sr-table tbody td:last-child { border-right: none; }
.sr-table tbody tr:nth-child(even) td { background: #fbfcfd; }
.sr-table tbody tr:hover td { background: #eaf2ff; }

/* Buttons inside table */
.sr-table .btn, .sr-table button {
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
    print("Receiving page CSS completely overwritten with exact Reports theme.")

"""Apply exact Reports page CSS to receiving.html."""
import io, os
path = os.path.join("modules", "lab", "templates", "lab", "receiving.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

new_css = """
<style>
/* =========================================================
   EXACT REPORTS THEME
   ========================================================= */
.sr-page {
  padding: 16px 24px 40px;
  font-family: 'Segoe UI', Arial, sans-serif;
  font-size: 0.95rem;
  color: #212529;
}

/* --- Header --- */
.sr-header {
  background: linear-gradient(135deg, #1a3d7c 0%, #0d6efd 100%);
  border-radius: 10px;
  padding: 16px 20px;
  margin-bottom: 20px;
  color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: flex-end; /* Align to bottom to match Reports */
  border: none;
}
.sr-title {
  font-size: 1.25rem;
  font-weight: 700;
  text-transform: uppercase;
  margin: 0;
  letter-spacing: 0.02em;
  color: #fff;
  display: flex;
  align-items: center;
  gap: 10px;
}
.sr-title i { color: #fff; }
.sr-sub {
  font-size: 0.85rem;
  color: #dbeafe;
  font-family: Consolas, Monaco, monospace;
  margin: 0;
  text-align: right; /* Puts it on the right side like "01-Oct-2026 to..." */
}

/* --- Filter Box --- */
.sr-filter {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 14px 16px;
  background: #fff;
  border: 1px solid #dee2e6;
  border-radius: 8px;
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
  flex: 1;
  max-width: 400px;
  height: 38px;
  padding: 0 12px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  background: #fff;
  color: #212529;
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
  cursor: pointer;
}

/* --- Yellow Band --- */
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
  display: flex;
  align-items: center;
  gap: 8px;
}

/* --- Table Card (Outer Dark Border) --- */
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

/* --- Table Headers --- */
.sr-table thead th {
  background: #1a3d7c;
  color: #fff;
  font-size: 0.82rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding: 12px 12px;
  text-align: center;
  border-bottom: 2px solid #212529;
  border-right: 1px solid #343a40;
  vertical-align: middle;
}
.sr-table thead th:last-child { border-right: none; }

/* --- Table Body (Light Borders) --- */
.sr-table tbody td {
  font-size: 0.9rem;
  padding: 10px 12px;
  border-bottom: 1px solid #dee2e6;
  border-right: 1px solid #f1f3f5;
  vertical-align: middle;
  color: #212529;
  background: #fff;
}
.sr-table tbody td:last-child { border-right: none; }
.sr-table tbody tr:nth-child(even) td { background: #fbfcfd; }
.sr-table tbody tr:hover td { background: #eaf2ff; }

/* --- Specific Element Styles --- */
.sr-table code {
  background: #eef4ff;
  color: #1a3d7c;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: Consolas, monospace;
  font-size: 0.85rem;
}
</style>
"""

# Replace the entire <style>...</style> block
start = src.find("<style>")
end = src.find("</style>") + len("</style>")
if start != -1 and end != -1:
    src = src[:start] + new_css + src[end:]
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("Exact Reports theme applied to receiving.html.")
else:
    print("Style block not found.")

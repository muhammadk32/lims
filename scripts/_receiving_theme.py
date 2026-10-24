"""Apply the exact same theme to receiving.html."""
import io, os

paths = [
    os.path.join("modules", "lab", "templates", "lab", "receiving.html"),
    os.path.join("modules", "lab", "templates", "lab", "receiving_list.html")
]

path = None
for p in paths:
    if os.path.exists(p):
        path = p
        break

if not path:
    print("receiving.html not found in expected paths.")
else:
    with io.open(path, "r", encoding="utf-8", newline="") as f:
        src = f.read()

    add = """
/* ===== MATCH TEST IN PROCESS THEME ===== */
.rec-page { padding: 16px 24px 40px !important; }

/* 1. Header */
.rec-header {
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
.rec-header h1, .rec-header .rec-title, .rec-header i { color: #fff !important; font-weight: 700 !important; text-transform: uppercase !important; font-size: 1.25rem !important; }
.rec-header .rec-sub { color: #dbeafe !important; font-family: Consolas, monospace !important; margin: 0 !important; }

/* 2. Search Box */
.rec-filter {
  display: flex !important;
  align-items: center !important;
  gap: 10px !important;
  padding: 14px 16px !important;
  background: #fff !important;
  border: 2px solid #212529 !important;
  border-radius: 8px !important;
  margin-bottom: 16px !important;
}
.rec-filter::before {
  content: "SEARCH" !important;
  background: transparent !important;
  color: #212529 !important;
  font-weight: 800 !important;
  font-size: 0.85rem !important;
  margin-right: 10px !important;
  position: static !important;
}
.rec-filter input {
  flex: 1 !important;
  max-width: 400px !important;
  border: 1px solid #212529 !important;
  border-radius: 4px !important;
  height: 38px !important;
  padding: 0 12px !important;
}
.rec-filter button, .rec-filter .btn {
  background: #198754 !important;
  border: 1px solid #198754 !important;
  color: #fff !important;
  font-weight: 700 !important;
  height: 38px !important;
  padding: 0 20px !important;
  border-radius: 4px !important;
}

/* 3. Yellow Band */
.rec-band {
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

/* 4. Table Card + Grid Borders */
.rec-card {
  border: 2px solid #212529 !important;
  border-radius: 6px !important;
  overflow: hidden !important;
  background: #fff !important;
  padding: 0 !important;
}
.rec-table {
  border-collapse: collapse !important;
  width: 100% !important;
  margin: 0 !important;
  border: 2px solid #212529 !important;
}
.rec-table thead th {
  border: 1px solid #212529 !important;
  background: #1a3d7c !important;
  color: #fff !important;
  text-align: center !important;
  padding: 12px 8px !important;
  font-size: 0.85rem !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
}
.rec-table tbody td {
  border: 1px solid #212529 !important;
  padding: 10px 12px !important;
  background: #fff !important;
}
.rec-table tbody tr:hover td {
  background: #eaf2ff !important;
}
"""

    # If classes are generic (e.g., .card, .table) fallback
    if "rec-page" not in src and "tip-page" not in src:
        print("Warning: rec-page class not found in receiving.html. Applying to generic containers.")

    idx = src.rfind("</style>")
    if idx > 0:
        if "/* ===== MATCH TEST IN PROCESS THEME ===== */" not in src:
            src = src[:idx] + add + src[idx:]
        else:
            start = src.find("/* ===== MATCH TEST IN PROCESS THEME ===== */")
            end = src.rfind("</style>")
            src = src[:start] + add + src[end:]
    else:
        # No style block, append one before endblock
        css = "<style>\n" + add + "\n</style>\n"
        idx = src.rfind("{% endblock %}")
        if idx > 0:
            src = src[:idx] + css + src[idx:]
        else:
            src += css

    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print(f"Theme applied to {path}")

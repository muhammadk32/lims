"""Professional restyle of rate list export page."""
import io, os
path = os.path.join("templates", "test_settings", "_rate_list_export.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

# replace whole <style> block
start = src.find("<style>")
end = src.find("</style>")
if start >= 0 and end > start:
    new_style = (
"<style>" + nl +
".rle-wrap { max-width:1200px; margin:0 auto; padding:12px; }" + nl +
"" + nl +
".rle-head {" + nl +
"  display:flex; justify-content:space-between; align-items:center;" + nl +
"  background:linear-gradient(135deg,#1a3d7c 0%,#0d6efd 100%);" + nl +
"  color:#fff; padding:14px 20px; border-radius:12px;" + nl +
"  margin-bottom:16px; box-shadow:0 4px 12px rgba(0,0,0,0.15);" + nl +
"}" + nl +
".rle-head h2 { font-size:1.25rem; margin:0; color:#fff; font-weight:700; letter-spacing:0.02em; }" + nl +
".rle-back {" + nl +
"  padding:7px 16px; border-radius:8px;" + nl +
"  background:#fff; color:#1a3d7c; text-decoration:none;" + nl +
"  font-weight:700; font-size:0.82rem;" + nl +
"  transition:all .12s;" + nl +
"}" + nl +
".rle-back:hover { background:#ffd166; color:#1a3d7c; }" + nl +
"" + nl +
".rle-filters {" + nl +
"  background:linear-gradient(135deg,#f8f9fa 0%,#e9ecef 100%);" + nl +
"  border:2px solid #1a3d7c; border-radius:12px;" + nl +
"  padding:18px; margin-bottom:16px;" + nl +
"  display:grid; grid-template-columns: repeat(4, 1fr); gap:14px 18px;" + nl +
"  box-shadow:0 2px 6px rgba(0,0,0,0.08);" + nl +
"}" + nl +
".rle-filters label {" + nl +
"  display:block; font-size:0.74rem; font-weight:800;" + nl +
"  text-transform:uppercase; color:#1a3d7c;" + nl +
"  margin-bottom:6px; letter-spacing:0.05em;" + nl +
"}" + nl +
".rle-filters select {" + nl +
"  width:100%; padding:8px 12px; border:2px solid #ced4da;" + nl +
"  border-radius:8px; font-size:0.9rem; background:#fff;" + nl +
"  transition:border .12s;" + nl +
"}" + nl +
".rle-filters select:focus { outline:none; border-color:#0d6efd; box-shadow:0 0 0 3px rgba(13,110,253,.15); }" + nl +
".rle-filters .actions {" + nl +
"  grid-column: 1 / -1; display:flex; gap:10px;" + nl +
"  justify-content:flex-end; margin-top:8px; padding-top:10px;" + nl +
"  border-top:1px dashed #adb5bd;" + nl +
"}" + nl +
".rle-btn {" + nl +
"  padding:8px 22px; border:2px solid #1a3d7c; border-radius:8px;" + nl +
"  background:#fff; color:#1a3d7c; font-weight:700;" + nl +
"  font-size:0.85rem; cursor:pointer; text-decoration:none;" + nl +
"  display:inline-flex; align-items:center; gap:6px;" + nl +
"  transition:all .12s;" + nl +
"}" + nl +
".rle-btn:hover { background:#1a3d7c; color:#fff; }" + nl +
".rle-btn-primary { background:linear-gradient(135deg,#1a3d7c 0%,#0d6efd 100%); border-color:#1a3d7c; color:#fff; }" + nl +
".rle-btn-primary:hover { filter:brightness(1.15); }" + nl +
".rle-btn:disabled { opacity:0.4; cursor:not-allowed; }" + nl +
"" + nl +
"/* ==== report card ==== */" + nl +
".rle-report {" + nl +
"  background:#fff; border:2px solid #1a3d7c; border-radius:14px;" + nl +
"  padding:24px 28px; box-shadow:0 4px 16px rgba(0,0,0,0.1);" + nl +
"  overflow:hidden;" + nl +
"}" + nl +
"" + nl +
".rle-brand {" + nl +
"  display:flex; align-items:center; gap:16px;" + nl +
"  border-bottom:3px solid #1a3d7c;" + nl +
"  padding-bottom:14px; margin-bottom:14px;" + nl +
"}" + nl +
".rle-brand img { height:64px; border-radius:8px; }" + nl +
".rle-brand .name {" + nl +
"  font-size:1.35rem; font-weight:800;" + nl +
"  letter-spacing:0.03em; color:#b81414;" + nl +
"  font-family:'Segoe UI', Arial, sans-serif;" + nl +
"}" + nl +
".rle-brand .sub {" + nl +
"  font-size:0.82rem; color:#6c757d; margin-top:2px;" + nl +
"}" + nl +
"" + nl +
".rle-report-title {" + nl +
"  display:inline-block; background:linear-gradient(135deg,#ffd166 0%,#ffb703 100%);" + nl +
"  color:#1a1a1a; font-size:0.95rem; font-weight:800;" + nl +
"  letter-spacing:0.04em; text-transform:uppercase;" + nl +
"  padding:8px 18px; border-radius:999px; margin:8px 0 16px;" + nl +
"  box-shadow:0 2px 6px rgba(0,0,0,0.15);" + nl +
"}" + nl +
"" + nl +
".rle-table {" + nl +
"  width:100%; border-collapse:separate; border-spacing:0;" + nl +
"  font-size:0.85rem; border:2px solid #1a3d7c;" + nl +
"  border-radius:12px; overflow:hidden;" + nl +
"}" + nl +
".rle-table thead th {" + nl +
"  background:linear-gradient(135deg,#1a3d7c 0%,#0d6efd 100%);" + nl +
"  color:#fff; padding:10px 12px;" + nl +
"  text-align:left; font-size:0.78rem; font-weight:700;" + nl +
"  text-transform:uppercase; letter-spacing:0.05em;" + nl +
"  border-right:1px solid rgba(255,255,255,0.2);" + nl +
"}" + nl +
".rle-table thead th:last-child { border-right:none; }" + nl +
".rle-table tbody td {" + nl +
"  padding:7px 12px; border-bottom:1px solid #dee2e6;" + nl +
"  border-right:1px solid #dee2e6;" + nl +
"  vertical-align:middle;" + nl +
"}" + nl +
".rle-table tbody td:last-child { border-right:none; }" + nl +
".rle-table tbody tr:last-child td { border-bottom:none; }" + nl +
".rle-table tbody tr:nth-child(even) td { background:#f5f9ff; }" + nl +
".rle-table tbody tr:hover td { background:#e7f1ff; }" + nl +
".rle-table .num { text-align:right; font-family:Consolas, Monaco, monospace; font-weight:600; }" + nl +
".rle-dept-row td {" + nl +
"  background:linear-gradient(135deg,#e7f1ff 0%,#d0e2ff 100%) !important;" + nl +
"  font-weight:800; text-transform:uppercase; font-size:0.82rem;" + nl +
"  padding:10px 12px; border-top:2px solid #1a3d7c;" + nl +
"  color:#1a3d7c; letter-spacing:0.04em;" + nl +
"}" + nl +
"" + nl +
".rle-print-hint {" + nl +
"  display:inline-block; background:#e7f1ff;" + nl +
"  color:#1a3d7c; font-size:0.82rem; font-weight:600;" + nl +
"  padding:6px 14px; border-radius:999px; margin-bottom:12px;" + nl +
"}" + nl +
"" + nl +
"@media print {" + nl +
"  .rle-filters, .rle-head, .rle-print-hint, .rle-back { display:none !important; }" + nl +
"  .rle-wrap { padding:0; }" + nl +
"  .rle-report { padding:0; border:none; box-shadow:none; }" + nl +
"  .rle-table thead th { background:#1a3d7c !important; -webkit-print-color-adjust: exact; color:#fff !important; }" + nl +
"  .rle-dept-row td { background:#e0e8f5 !important; -webkit-print-color-adjust: exact; }" + nl +
"  .rle-table tbody tr:nth-child(even) td { background:#f5f7fa !important; -webkit-print-color-adjust: exact; }" + nl +
"  .rle-report-title { background:#ffd166 !important; -webkit-print-color-adjust: exact; }" + nl +
"}" + nl +
"</style>"
    )
    src = src[:start] + new_style + src[end + len("</style>"):]
    print("styles replaced")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

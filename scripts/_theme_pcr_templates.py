"""Theme PCR templates page — extend inline style."""
import io, os
path = os.path.join("templates", "settings", "pcr_templates.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

extra = (
"/* ===== Theme overrides ===== */" + nl +
".pt-header {" + nl +
"  background: linear-gradient(135deg, #1a3d7c 0%, #0d6efd 100%) !important;" + nl +
"  color: #fff !important;" + nl +
"  padding: 14px 20px !important;" + nl +
"  border-radius: 12px !important;" + nl +
"  border: 2px solid #1a3d7c !important;" + nl +
"  border-bottom: 2px solid #1a3d7c !important;" + nl +
"  box-shadow: 0 4px 12px rgba(0,0,0,0.12);" + nl +
"  margin-bottom: 14px !important;" + nl +
"}" + nl +
".pt-title," + nl +
".pt-title i { color: #fff !important; }" + nl +
".pt-title i { color: #ffd166 !important; }" + nl +
".pt-sub { color: rgba(255,255,255,0.9) !important; }" + nl +
"" + nl +
".pt-picker {" + nl +
"  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%) !important;" + nl +
"  border: 2px solid #1a3d7c !important;" + nl +
"  border-radius: 12px !important;" + nl +
"  box-shadow: 0 2px 6px rgba(0,0,0,0.06);" + nl +
"  padding: 14px 16px !important;" + nl +
"}" + nl +
".pt-picker label { color: #1a3d7c !important; font-weight: 800 !important; }" + nl +
".pt-picker select {" + nl +
"  border: 2px solid #ced4da !important;" + nl +
"  border-radius: 8px !important;" + nl +
"  padding: 6px 10px !important;" + nl +
"  height: 36px !important;" + nl +
"}" + nl +
".pt-picker select:focus {" + nl +
"  outline: none; border-color: #0d6efd !important;" + nl +
"  box-shadow: 0 0 0 3px rgba(13,110,253,0.15) !important;" + nl +
"}" + nl +
"" + nl +
".pt-btn {" + nl +
"  border: 2px solid #1a3d7c !important;" + nl +
"  border-radius: 8px !important;" + nl +
"  background: #fff !important;" + nl +
"  color: #1a3d7c !important;" + nl +
"  font-weight: 700 !important;" + nl +
"  padding: 6px 18px !important;" + nl +
"  height: 36px !important;" + nl +
"  transition: all .12s;" + nl +
"}" + nl +
".pt-btn:hover { background: #1a3d7c !important; color: #fff !important; }" + nl +
".pt-btn-primary {" + nl +
"  background: linear-gradient(135deg, #1a3d7c 0%, #0d6efd 100%) !important;" + nl +
"  border-color: #1a3d7c !important;" + nl +
"  color: #fff !important;" + nl +
"}" + nl +
".pt-btn-primary:hover { filter: brightness(1.15); }" + nl +
"" + nl +
"/* Empty state box */" + nl +
".pt-empty {" + nl +
"  border: 2px dashed #1a3d7c !important;" + nl +
"  border-radius: 12px !important;" + nl +
"  background: #f0f4ff !important;" + nl +
"  color: #1a3d7c !important;" + nl +
"  padding: 24px !important;" + nl +
"  font-weight: 600;" + nl +
"}" + nl
)

# insert before closing </style>
close = "</style>"
if "/* ===== Theme overrides ===== */" not in src:
    src = src.replace(close, extra + close, 1)
    print("theme overrides added")
else:
    print("already present")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

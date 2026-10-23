"""Add dark borders to every box on bulk page."""
import io, os
path = os.path.join("templates", "test_settings", "_bulk.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

# Find the closing </style> and inject extra CSS just before it
extra_css = (
"/* ===== universal dark borders ===== */" + nl +
".bi-hero { border:2px solid #1a3d7c !important; }" + nl +
".bi-step { border:2px solid #1a3d7c !important; }" + nl +
".bi-info { border:2px solid #664d03 !important; border-left:5px solid #ffc107 !important; }" + nl +
".bi-upload { border:2.5px dashed #495057 !important; }" + nl +
".bi-upload:hover { border-color:#0d6efd !important; border-style:solid !important; }" + nl +
".bi-upload.dragover { border-color:#0d6efd !important; border-style:solid !important; }" + nl +
".bi-btn { border:2px solid #1a3d7c !important; }" + nl +
".bi-btn-primary { border-color:#0d6efd !important; }" + nl +
".bi-footer { border-top:2px solid #1a3d7c !important; }" + nl +
"#bulkForm { border:2px solid #1a3d7c; border-radius:12px; padding:18px; background:#fff; box-shadow:0 2px 8px rgba(0,0,0,0.08); margin-top:12px; }" + nl +
"/* footer button border */" + nl +
"#importBtn { border:2px solid #0d6efd !important; }" + nl +
"" + nl
)

close_style = "</style>"
if "universal dark borders" not in src:
    src = src.replace(close_style, extra_css + close_style, 1)
    print("universal borders added")
else:
    print("already present")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

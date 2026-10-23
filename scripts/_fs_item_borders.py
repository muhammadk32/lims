"""Reception Form: borders on .fs-item field rows."""
import io, os
path = os.path.join("templates", "form_settings", "index.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

add = (
"/* ===== Bordered field items ===== */" + nl +
".fs-item {" + nl +
"  border: 1.5px solid #212529 !important;" + nl +
"  border-radius: 6px !important;" + nl +
"  padding: 8px 12px !important;" + nl +
"  margin: 4px 0 !important;" + nl +
"  background: #fff !important;" + nl +
"  min-height: 42px !important;" + nl +
"  display: flex !important;" + nl +
"  align-items: center !important;" + nl +
"  gap: 10px !important;" + nl +
"}" + nl +
".fs-item:hover {" + nl +
"  background: #f5f9ff !important;" + nl +
"  border-color: #0d6efd !important;" + nl +
"}" + nl +
".fs-item .name, .fs-item .lbl, .fs-item label:not(.form-check-label) {" + nl +
"  font-weight: 700 !important;" + nl +
"  font-size: 0.85rem !important;" + nl +
"  text-transform: uppercase !important;" + nl +
"  letter-spacing: 0.02em !important;" + nl +
"  color: #212529 !important;" + nl +
"}" + nl +
"/* Slightly larger toggle switches */" + nl +
".fs-item .vis-toggle.form-check-input," + nl +
".fs-item .form-check-input {" + nl +
"  width: 2.2em !important;" + nl +
"  height: 1.15em !important;" + nl +
"  border: 2px solid #212529 !important;" + nl +
"}" + nl +
".fs-item .form-check-input:checked {" + nl +
"  background-color: #0d6efd !important;" + nl +
"  border-color: #1a3d7c !important;" + nl +
"}" + nl
)

idx = src.rfind("</style>")
if ".fs-item {" not in src.split("</style>")[0]:
    if idx > 0:
        src = src[:idx] + add + src[idx:]
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(src)
        print("fs-item borders added")
else:
    print("no </style> or already present")

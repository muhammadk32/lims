"""Reception Form: dark border around every field row."""
import io, os
path = os.path.join("templates", "form_settings", "index.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

add = (
"/* ===== Borders on every field row inside fs-sec ===== */" + nl +
".fs-sec .right, .fs-sec .fields, .fs-sec .body {" + nl +
"  padding: 6px 8px !important;" + nl +
"}" + nl +
".fs-sec .row, .fs-sec .field-row, .fs-sec .fs-field, .fs-sec .fs-row," + nl +
".fs-sec .form-check, .fs-sec .field {" + nl +
"  border: 1.5px solid #212529 !important;" + nl +
"  border-radius: 6px !important;" + nl +
"  padding: 8px 12px !important;" + nl +
"  margin-bottom: 6px !important;" + nl +
"  background: #fff !important;" + nl +
"  min-height: 42px !important;" + nl +
"  display: flex !important;" + nl +
"  align-items: center !important;" + nl +
"  gap: 8px !important;" + nl +
"}" + nl +
".fs-sec .row:hover, .fs-sec .field-row:hover, .fs-sec .fs-field:hover," + nl +
".fs-sec .fs-row:hover, .fs-sec .field:hover {" + nl +
"  background: #f5f9ff !important;" + nl +
"  border-color: #0d6efd !important;" + nl +
"}" + nl +
"/* Remove the old bottom-only separator */" + nl +
".fs-sec .row:last-child, .fs-sec .field-row:last-child," + nl +
".fs-sec .fs-field:last-child, .fs-sec .fs-row:last-child {" + nl +
"  margin-bottom: 0 !important;" + nl +
"}" + nl
)

idx = src.rfind("</style>")
if "Borders on every field row inside fs-sec" not in src and idx > 0:
    src = src[:idx] + add + src[idx:]
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("field borders added")
else:
    print("no </style> or already present")

"""Reception Form Settings — polish using fs-* classes."""
import io, os
path = os.path.join("templates", "form_settings", "index.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

add = (
"/* ===== Reception Form: polish theme ===== */" + nl +
".fs-page { max-width: 100% !important; padding: 12px 20px 24px !important; }" + nl +
"" + nl +
"/* Top header → blue gradient banner */" + nl +
".fs-top {" + nl +
"  background: linear-gradient(135deg, #1a3d7c 0%, #0d6efd 100%) !important;" + nl +
"  color: #fff !important;" + nl +
"  padding: 14px 20px !important;" + nl +
"  border-radius: 12px !important;" + nl +
"  border: 2px solid #1a3d7c !important;" + nl +
"  margin-bottom: 16px !important;" + nl +
"  box-shadow: 0 4px 12px rgba(0,0,0,0.12) !important;" + nl +
"  align-items: center !important;" + nl +
"  border-bottom: 2px solid #1a3d7c !important;" + nl +
"}" + nl +
".fs-top h3 { color: #fff !important; }" + nl +
".fs-top h3 i { color: #ffd166 !important; }" + nl +
".fs-top .subtitle { color: rgba(255,255,255,0.9) !important; }" + nl +
".fs-top .stats { color: rgba(255,255,255,0.9) !important; }" + nl +
".fs-top .presets .lbl { color: #ffd166 !important; }" + nl +
".fs-top .presets button {" + nl +
"  background: #fff !important;" + nl +
"  color: #1a3d7c !important;" + nl +
"  border: 2px solid #fff !important;" + nl +
"  border-radius: 6px !important;" + nl +
"  font-weight: 700 !important;" + nl +
"}" + nl +
".fs-top .presets button:hover {" + nl +
"  background: #ffd166 !important;" + nl +
"  border-color: #ffd166 !important;" + nl +
"  color: #1a1a1a !important;" + nl +
"}" + nl +
".fs-top .preview-btn {" + nl +
"  background: #fff !important;" + nl +
"  color: #1a3d7c !important;" + nl +
"  border: 2px solid #fff !important;" + nl +
"  border-radius: 6px !important;" + nl +
"  font-weight: 700 !important;" + nl +
"  padding: 6px 14px !important;" + nl +
"  text-decoration: none !important;" + nl +
"}" + nl +
".fs-top .preview-btn:hover { background: #ffd166 !important; border-color: #ffd166 !important; }" + nl +
"" + nl +
"/* Each section: rounded bordered card */" + nl +
".fs-sec {" + nl +
"  background: #fff !important;" + nl +
"  border: 2px solid #212529 !important;" + nl +
"  border-radius: 10px !important;" + nl +
"  margin-bottom: 10px !important;" + nl +
"  overflow: hidden !important;" + nl +
"  box-shadow: 0 1px 4px rgba(0,0,0,0.05) !important;" + nl +
"}" + nl +
".fs-sec .left {" + nl +
"  background: linear-gradient(135deg, #1a3d7c 0%, #0d6efd 100%) !important;" + nl +
"  color: #fff !important;" + nl +
"  padding: 10px 14px !important;" + nl +
"  border-radius: 8px 8px 0 0 !important;" + nl +
"  border-bottom: 2px solid #212529 !important;" + nl +
"  display: flex !important;" + nl +
"  align-items: center !important;" + nl +
"  gap: 10px !important;" + nl +
"}" + nl +
".fs-sec .left .title { color: #fff !important; font-weight: 800 !important; text-transform: uppercase !important; letter-spacing: 0.04em !important; }" + nl +
".fs-sec .left .title i { color: #ffd166 !important; }" + nl +
"" + nl +
"/* Field rows inside */" + nl +
".fs-fields, .fs-field-rows {" + nl +
"  padding: 8px 12px !important;" + nl +
"}" + nl +
".fs-field, .fs-row {" + nl +
"  border-bottom: 1px solid #dee2e6 !important;" + nl +
"  padding: 8px 6px !important;" + nl +
"}" + nl +
".fs-field:last-child, .fs-row:last-child { border-bottom: none !important; }" + nl +
".fs-field:hover, .fs-row:hover { background: #f5f9ff !important; }" + nl +
".fs-field label, .fs-row label {" + nl +
"  font-weight: 700 !important;" + nl +
"  font-size: 0.85rem !important;" + nl +
"  text-transform: uppercase !important;" + nl +
"  letter-spacing: 0.03em !important;" + nl +
"  color: #212529 !important;" + nl +
"}" + nl +
"" + nl +
"/* Toggle switches → brand blue */" + nl +
".fs-sec .form-check-input:checked {" + nl +
"  background-color: #0d6efd !important;" + nl +
"  border-color: #1a3d7c !important;" + nl +
"}" + nl +
"" + nl +
"/* Save button */" + nl +
".fs-page .btn-save, .fs-page button[type=\"submit\"]:not(.presets button) {" + nl +
"  background: linear-gradient(135deg, #198754 0%, #20c997 100%) !important;" + nl +
"  border: 2px solid #198754 !important;" + nl +
"  color: #fff !important;" + nl +
"  font-weight: 700 !important;" + nl +
"  font-size: 0.88rem !important;" + nl +
"  padding: 10px 26px !important;" + nl +
"  border-radius: 8px !important;" + nl +
"  box-shadow: 0 2px 6px rgba(25,135,84,0.25) !important;" + nl +
"}" + nl
)

idx = src.rfind("</style>")
if "Reception Form: polish theme" not in src and idx > 0:
    src = src[:idx] + add + src[idx:]
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("fs-* polish added")
else:
    print("no </style> or already present")

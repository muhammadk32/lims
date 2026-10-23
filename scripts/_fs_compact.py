"""Compact section headers + icon alignment."""
import io, os
path = os.path.join("templates", "form_settings", "index.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== Compact headers + field rows ===== */
.fs-sec .left {
  padding: 8px 14px !important;
  min-height: 40px !important;
  gap: 8px !important;
}
.fs-sec .left .title {
  font-size: 0.82rem !important;
  display: inline-flex !important;
  align-items: center !important;
  gap: 6px !important;
}
.fs-sec .left .title i {
  font-size: 0.9rem !important;
  line-height: 1 !important;
}
/* Field rows: shorter */
.fs-item {
  padding: 6px 10px !important;
  min-height: 34px !important;
  margin: 3px 0 !important;
}
.fs-item label:not(.form-check-label),
.fs-item .name, .fs-item .lbl {
  font-size: 0.8rem !important;
  line-height: 1.2 !important;
}
.fs-item .form-check-input {
  width: 2em !important;
  height: 1.05em !important;
  margin-top: 0 !important;
}
"""

idx = src.rfind("</style>")
if idx > 0:
    src = src[:idx] + add + src[idx:]
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("compact styles added")

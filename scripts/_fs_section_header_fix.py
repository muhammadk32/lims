"""Fix section header width — full row."""
import io, os
path = os.path.join("templates", "form_settings", "index.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== Section header full width ===== */
.fs-sec {
  display: flex !important;
  width: 100% !important;
  padding: 0 !important;
}
.fs-sec .left {
  width: 100% !important;
  display: flex !important;
  justify-content: flex-start !important;
  align-items: center !important;
  gap: 12px !important;
  padding: 10px 16px !important;
  background: linear-gradient(135deg, #1a3d7c 0%, #0d6efd 100%) !important;
  border-radius: 8px !important;
  color: #fff !important;
}
.fs-sec .left .title {
  color: #fff !important;
  font-weight: 800 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.04em !important;
  font-size: 0.9rem !important;
}
.fs-sec .left .title i {
  color: #ffd166 !important;
}
/* Count badge */
.fs-sec .left .count,
.fs-sec .left .badge {
  background: #ffd166 !important;
  color: #1a1a1a !important;
  font-weight: 800 !important;
  padding: 3px 10px !important;
  border-radius: 999px !important;
  font-size: 0.72rem !important;
  margin-left: auto !important;
}
"""

idx = src.rfind("</style>")
if idx > 0:
    src = src[:idx] + add + src[idx:]
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("section header fixed")

"""Nuclear override: force blue gradient on ALL thead th everywhere in Lab Test Settings."""
import io, os
path = os.path.join("static", "css", "test_settings_theme.css")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

css = """
/* ===== NUCLEAR: every thead th in test settings, no exceptions ===== */
.lts-content thead th,
.lts-page thead th,
.lt-page thead th,
.lt-page thead > tr > th,
.lts-content thead > tr > th {
  background: linear-gradient(135deg, #1a3d7c 0%, #0d6efd 100%) !important;
  background-color: #1a3d7c !important;
  background-image: linear-gradient(135deg, #1a3d7c 0%, #0d6efd 100%) !important;
  color: #ffffff !important;
  border-top: 2px solid #212529 !important;
  border-bottom: 2px solid #212529 !important;
  border-right: 1px solid #212529 !important;
  border-left: none !important;
  padding: 10px 12px !important;
  text-transform: uppercase;
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.05em;
  box-shadow: none !important;
  text-shadow: none !important;
}
.lts-content thead th:last-child,
.lts-page thead th:last-child,
.lt-page thead th:last-child,
.lts-content thead > tr > th:last-child {
  border-right: 2px solid #212529 !important;
}
.lts-content thead th.num,
.lts-content thead th.center,
.lts-content thead th.end,
.lts-content thead th[class] {
  background: linear-gradient(135deg, #1a3d7c 0%, #0d6efd 100%) !important;
  background-color: #1a3d7c !important;
  color: #ffffff !important;
}
"""

# remove any previous "NUCLEAR" block to avoid stacking
if "NUCLEAR: every thead th" in src:
    import re
    src = re.sub(r'/\* =+ NUCLEAR:.*?(?=/\* =+|$)', '', src, flags=re.DOTALL)
    print("removed previous NUCLEAR block")

src = src + "\n" + css
with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("NUCLEAR override added")

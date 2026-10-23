"""Force ALL column headers to blue gradient in Lab Test Settings."""
import io, os
path = os.path.join("static", "css", "test_settings_theme.css")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

css = """
/* ===== absolute override: every thead th in Lab Test Settings ===== */
.lts-content table thead th,
.lt-page table thead th,
.lts-page table thead th {
  background: linear-gradient(135deg, #1a3d7c 0%, #0d6efd 100%) !important;
  color: #fff !important;
  border-right: 1px solid #212529 !important;
  border-bottom: 2px solid #212529 !important;
  border-top: none !important;
  border-left: none !important;
  padding: 10px 12px !important;
  text-transform: uppercase;
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.05em;
}
.lts-content table thead th:last-child,
.lt-page table thead th:last-child,
.lts-page table thead th:last-child {
  border-right: none !important;
}
"""

if "absolute override: every thead th" not in src:
    src = src + "\n" + css
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("universal th override added")
else:
    print("already present")

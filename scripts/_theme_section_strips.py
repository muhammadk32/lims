"""Theme the format-tab strip + section headers."""
import io, os
path = os.path.join("static", "css", "test_settings_theme.css")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

css = """
/* ===== section strip bars above tables (formats, panels, etc.) ===== */
.tf-section, .ts-section, .rl-section, .fmt-strip {
  background: linear-gradient(135deg, #1a3d7c 0%, #0d6efd 100%) !important;
  color: #fff !important;
  border-radius: 10px 10px 0 0 !important;
  padding: 10px 16px !important;
  border: 2px solid #212529 !important;
  border-bottom: none !important;
  font-weight: 800 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.05em !important;
  font-size: 0.82rem !important;
}
/* generic fallback: any dark strip immediately above a table */
.lts-content > div > div[style*="background:#1a1a1a"],
.lts-content > div > div[style*="background: #1a1a1a"],
.lts-content > div > div[style*="#1a1a1a"] {
  background: linear-gradient(135deg, #1a3d7c 0%, #0d6efd 100%) !important;
  color: #fff !important;
  border-radius: 10px 10px 0 0 !important;
}
"""

if "section strip bars above tables" not in src:
    src = src + "\n" + css
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("section strip override added")
else:
    print("already present")

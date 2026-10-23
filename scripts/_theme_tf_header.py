"""Add tf-header + tf-title + tf-filter to theme."""
import io, os
path = os.path.join("static", "css", "test_settings_theme.css")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

css = """
/* ===== Test Formats tab header ===== */
.tf-header {
  background: linear-gradient(135deg, #1a3d7c 0%, #0d6efd 100%) !important;
  color: #fff !important;
  padding: 14px 20px !important;
  border-radius: 12px !important;
  border: 2px solid #1a3d7c !important;
  margin-bottom: 14px !important;
  box-shadow: 0 4px 12px rgba(0,0,0,0.12) !important;
}
.tf-header .tf-title,
.tf-header .tf-title i {
  color: #fff !important;
}
.tf-header .tf-title i { color: #ffd166 !important; }
.tf-header .tf-subtitle,
.tf-header .tf-count {
  color: #fff !important;
  opacity: 0.92;
}

/* ===== Test Formats filter strip ===== */
.tf-filter {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%) !important;
  border: 2px solid #1a3d7c !important;
  border-radius: 12px !important;
  box-shadow: 0 2px 6px rgba(0,0,0,0.06) !important;
}

/* Also cover .rl-header (rate detail/edit) and rdg/rle variants */
.rl-header, .rle-head, .rdg-head, .rlk-header {
  background: linear-gradient(135deg, #1a3d7c 0%, #0d6efd 100%) !important;
  color: #fff !important;
  padding: 14px 20px !important;
  border-radius: 12px !important;
  border: 2px solid #1a3d7c !important;
  margin-bottom: 14px !important;
  box-shadow: 0 4px 12px rgba(0,0,0,0.12) !important;
}
.rl-header h2, .rle-head h2, .rdg-head h2,
.rl-header h1, .rle-head h1, .rdg-head h1 {
  color: #fff !important;
}
.rl-header i, .rle-head i, .rdg-head i {
  color: #ffd166 !important;
}
"""

if ".tf-header {" not in src:
    src = src + "\n" + css
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("tf-header theme added")
else:
    print("already present")

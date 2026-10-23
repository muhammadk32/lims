"""Theme format previews header + cards."""
import io, os
path = os.path.join("static", "css", "test_settings_theme.css")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

css = """
/* ===== Format Previews header ===== */
.fp-header {
  background: linear-gradient(135deg, #1a3d7c 0%, #0d6efd 100%) !important;
  color: #fff !important;
  padding: 14px 20px !important;
  border-radius: 12px !important;
  border: 2px solid #1a3d7c !important;
  margin-bottom: 14px !important;
  box-shadow: 0 4px 12px rgba(0,0,0,0.12) !important;
  display: flex; align-items: center; justify-content: space-between;
}
.fp-header .fp-title,
.fp-header .fp-title i {
  color: #fff !important;
}
.fp-header .fp-title i { color: #ffd166 !important; }
.fp-header .fp-subtitle {
  color: rgba(255,255,255,0.9) !important;
}
.fp-header .fp-btn-primary {
  background: #fff !important;
  color: #1a3d7c !important;
  border: 2px solid #fff !important;
  font-weight: 700;
}
.fp-header .fp-btn-primary:hover {
  background: #ffd166 !important;
  border-color: #ffd166 !important;
  color: #1a1a1a !important;
}

/* ===== Format Preview cards ===== */
.fp-card {
  background: #fff !important;
  border: 2px solid #212529 !important;
  border-radius: 12px !important;
  overflow: hidden !important;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
  margin-bottom: 12px;
}
.fp-card-hd {
  background: linear-gradient(135deg, #1a3d7c 0%, #0d6efd 100%) !important;
  color: #fff !important;
  padding: 10px 14px !important;
  font-weight: 800 !important;
  font-size: 0.86rem !important;
  text-transform: uppercase !important;
  letter-spacing: 0.04em;
  border-bottom: 2px solid #212529 !important;
  display: flex; align-items: center; justify-content: space-between;
}
.fp-card-hd .fp-tag {
  background: #ffd166 !important;
  color: #1a1a1a !important;
  padding: 2px 10px !important;
  border-radius: 999px !important;
  font-size: 0.66rem !important;
  font-weight: 800 !important;
}
.fp-card-bd {
  padding: 12px 16px !important;
}
.fp-card-bd .fp-row {
  border-bottom: 1px solid #dee2e6 !important;
  padding: 6px 0 !important;
}
.fp-card-bd .fp-row:last-child {
  border-bottom: none !important;
}
.fp-card-ft {
  background: #f7f9fc !important;
  border-top: 2px solid #212529 !important;
  padding: 8px 14px !important;
  font-size: 0.78rem !important;
  color: #495057 !important;
}
"""

if ".fp-header {" not in src:
    src = src + "\n" + css
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("format previews theme added")
else:
    print("already present")

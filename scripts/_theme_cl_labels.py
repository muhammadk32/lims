"""Theme culture labels page — cl-* classes."""
import io, os
path = os.path.join("static", "css", "admin_theme.css")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

css = """
/* ===== Culture Labels page (cl-* classes) ===== */
.cl-header {
  background: linear-gradient(135deg, #1a3d7c 0%, #0d6efd 100%) !important;
  color: #fff !important;
  padding: 14px 20px !important;
  border-radius: 12px !important;
  border: 2px solid #1a3d7c !important;
  margin-bottom: 14px !important;
  box-shadow: 0 4px 12px rgba(0,0,0,0.12) !important;
}
.cl-title, .cl-title i { color: #fff !important; }
.cl-title i { color: #ffd166 !important; }
.cl-sub { color: rgba(255,255,255,0.9) !important; }
.cl-btn {
  background: #fff !important;
  color: #1a3d7c !important;
  border: 2px solid #fff !important;
  border-radius: 8px !important;
  font-weight: 700 !important;
  padding: 7px 16px !important;
}
.cl-btn:hover {
  background: #ffd166 !important;
  border-color: #ffd166 !important;
  color: #1a1a1a !important;
}

.cl-card {
  background: #fff !important;
  border: 2px solid #212529 !important;
  border-radius: 12px !important;
  padding: 24px 28px !important;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
}

.cl-row {
  margin-bottom: 14px;
}
.cl-lbl {
  display: block !important;
  font-weight: 800 !important;
  font-size: 0.78rem !important;
  text-transform: uppercase !important;
  letter-spacing: 0.05em !important;
  color: #1a3d7c !important;
  margin-bottom: 6px !important;
}

.cl-input {
  width: 100% !important;
  padding: 8px 12px !important;
  border: 2px solid #ced4da !important;
  border-radius: 8px !important;
  font-size: 0.92rem !important;
  background: #fff !important;
}
.cl-input:focus {
  outline: none;
  border-color: #0d6efd !important;
  box-shadow: 0 0 0 3px rgba(13,110,253,0.15) !important;
}

.cl-hint {
  font-size: 0.74rem !important;
  color: #6c757d !important;
  margin-top: 4px;
  font-style: italic;
}

/* Save / Cancel buttons inside form */
.cl-card .btn,
.cl-card button[type="submit"] {
  border-radius: 8px !important;
  font-weight: 700 !important;
  padding: 8px 22px !important;
}
"""

if ".cl-header {" not in src:
    src = src + "\n" + css
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("cl-* theme added")
else:
    print("already present")

"""Theme Bootstrap-based report pages (billing, analytics)."""
import io, os
path = os.path.join("static", "css", "admin_theme.css")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

css = """
/* ===== Report pages: Bootstrap cards → themed ===== */
.app-content .container .card {
  border: 2px solid #212529 !important;
  border-radius: 12px !important;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
}
.app-content .container .card-body {
  padding: 24px 28px !important;
}
.app-content .container h3,
.app-content .container h2 {
  font-weight: 800 !important;
  letter-spacing: 0.02em;
}
.app-content .container h3 i,
.app-content .container h2 i {
  color: #1a3d7c !important;
}
.app-content .container .text-muted {
  color: #6c757d !important;
}
/* Input fields → dark border, rounded */
.app-content .container .form-control,
.app-content .container .form-select {
  border: 2px solid #212529 !important;
  border-radius: 8px !important;
  padding: 8px 12px !important;
}
.app-content .container .form-control:focus {
  border-color: #0d6efd !important;
  box-shadow: 0 0 0 3px rgba(13,110,253,0.15) !important;
}
/* Report submit button */
.app-content .container .btn-primary {
  background: linear-gradient(135deg, #1a3d7c 0%, #0d6efd 100%) !important;
  border: 2px solid #1a3d7c !important;
  border-radius: 8px !important;
  font-weight: 700 !important;
}
.app-content .container .btn-primary:hover {
  filter: brightness(1.15);
}
/* Labels */
.app-content .container .form-label {
  font-weight: 700 !important;
  font-size: 0.8rem !important;
  text-transform: uppercase !important;
  letter-spacing: 0.05em !important;
  color: #1a3d7c !important;
}
"""

if "Report pages: Bootstrap cards" not in src:
    src = src + "\n" + css
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("report page styles added")
else:
    print("already present")

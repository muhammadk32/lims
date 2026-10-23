"""Polish culture labels form + general admin form fields."""
import io, os
path = os.path.join("static", "css", "admin_theme.css")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

css = """
/* ===== Admin form cards (culture labels, references, etc.) ===== */
.branding-form, .labels-form, .settings-form,
form[method="POST"] > .card,
.card-body {
  border-radius: 12px;
}

/* Form labels: uppercase, colored */
.form-label,
label.form-label {
  font-weight: 800 !important;
  font-size: 0.78rem !important;
  text-transform: uppercase !important;
  letter-spacing: 0.05em !important;
  color: #1a3d7c !important;
}

/* Form inputs = 2px border + focus ring */
.form-control, .form-select, textarea.form-control {
  border: 2px solid #ced4da !important;
  border-radius: 8px !important;
  padding: 8px 12px !important;
  font-size: 0.92rem;
}
.form-control:focus, .form-select:focus, textarea.form-control:focus {
  border-color: #0d6efd !important;
  box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.15) !important;
}

/* Form helper text */
.form-text, small.text-muted {
  font-size: 0.74rem !important;
  color: #6c757d !important;
}

/* Save button (primary) */
.btn-success {
  background: linear-gradient(135deg, #198754 0%, #20c997 100%) !important;
  border: 2px solid #198754 !important;
  color: #fff !important;
  font-weight: 700 !important;
  border-radius: 8px !important;
  padding: 8px 22px !important;
}
.btn-success:hover {
  filter: brightness(1.15);
}

/* Cancel / secondary buttons */
.btn-outline-secondary, .btn-light {
  border: 2px solid #495057 !important;
  border-radius: 8px !important;
  font-weight: 700 !important;
  color: #495057 !important;
  padding: 8px 22px !important;
}
.btn-outline-secondary:hover {
  background: #495057 !important;
  color: #fff !important;
}

/* Card wrapper around forms */
.row.g-3, .row.gy-3 {
  background: #fff;
  border: 2px solid #212529;
  border-radius: 12px;
  padding: 20px;
}
"""

if "Admin form cards (culture labels" not in src:
    src = src + "\n" + css
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("form theme added")
else:
    print("already present")

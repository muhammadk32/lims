"""Theme antibiotics page action buttons + inputs."""
import io, os
path = os.path.join("static", "css", "admin_theme.css")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

css = """
/* ===== Antibiotics page: action buttons ===== */
.ab-btn, .ab-edit, .ab-delete, .ab-toggle,
table td .btn-edit, table td .btn-delete, table td .btn-toggle,
table td a.btn, table td button.btn {
  border-radius: 8px !important;
  font-weight: 700 !important;
  font-size: 0.74rem !important;
  padding: 6px 12px !important;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  border-width: 2px !important;
  transition: all .12s;
  text-decoration: none !important;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

/* Edit = blue outline */
table td .btn-edit,
table td a[href*="/edit"],
table td button[onclick*="edit"],
.ab-edit {
  background: #fff !important;
  color: #0d6efd !important;
  border: 2px solid #0d6efd !important;
}
table td .btn-edit:hover,
table td a[href*="/edit"]:hover,
table td button[onclick*="edit"]:hover,
.ab-edit:hover {
  background: #0d6efd !important;
  color: #fff !important;
}

/* Deactivate / toggle = amber */
table td .btn-toggle,
table td button[onclick*="toggle"],
table td button[onclick*="deactivate"],
.ab-toggle {
  background: #fff !important;
  color: #b8860b !important;
  border: 2px solid #ffc107 !important;
}
table td .btn-toggle:hover,
table td button[onclick*="toggle"]:hover,
table td button[onclick*="deactivate"]:hover,
.ab-toggle:hover {
  background: #ffc107 !important;
  color: #1a1a1a !important;
}

/* Delete = red outline */
table td .btn-delete,
table td button[onclick*="delete"],
table td button[onclick*="Delete"],
.ab-delete {
  background: #fff !important;
  color: #dc3545 !important;
  border: 2px solid #dc3545 !important;
}
table td .btn-delete:hover,
table td button[onclick*="delete"]:hover,
table td button[onclick*="Delete"]:hover,
.ab-delete:hover {
  background: #dc3545 !important;
  color: #fff !important;
}

/* Search input on antibiotics (and any admin search field) */
.admin-content input[type="text"],
.admin-content input[type="search"],
.admin-content .search-input {
  border: 2px solid #1a1a1a !important;
  border-radius: 8px !important;
  padding: 8px 12px !important;
  font-size: 0.9rem !important;
  background: #fff !important;
}
.admin-content input[type="text"]:focus,
.admin-content input[type="search"]:focus {
  border-color: #0d6efd !important;
  box-shadow: 0 0 0 3px rgba(13,110,253,0.15) !important;
}

/* Search + Add buttons next to input */
.admin-content .btn-search,
.admin-content button[onclick*="search"],
.admin-content .btn-add {
  border-radius: 8px !important;
  border: 2px solid #198754 !important;
  background: #198754 !important;
  color: #fff !important;
  font-weight: 700 !important;
  padding: 8px 16px !important;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  font-size: 0.78rem !important;
}
.admin-content .btn-search:hover,
.admin-content button[onclick*="search"]:hover,
.admin-content .btn-add:hover {
  filter: brightness(1.15);
}

/* Form fields inside modals on this page */
.modal-body .form-control,
.modal-body .form-select {
  border: 2px solid #ced4da !important;
  border-radius: 8px !important;
  padding: 8px 12px !important;
}
"""

if "Antibiotics page: action buttons" not in src:
    src = src + "\n" + css
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("antibiotics button theme added")
else:
    print("already present")

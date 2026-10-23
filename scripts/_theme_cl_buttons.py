"""Theme culture labels page action buttons."""
import io, os
path = os.path.join("static", "css", "admin_theme.css")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

css = """
/* ===== Culture Labels action buttons (form footer) ===== */
.cl-card .cl-actions,
.cl-card .form-actions,
.cl-card .actions,
.cl-card > div:last-child {
  padding-top: 16px;
  margin-top: 16px;
  border-top: 2px solid #dee2e6;
}

/* Save Labels — primary */
.cl-card button[type="submit"],
.cl-card .btn-save,
.cl-card .cl-btn-save {
  background: linear-gradient(135deg, #1a3d7c 0%, #0d6efd 100%) !important;
  color: #fff !important;
  border: 2px solid #1a3d7c !important;
  border-radius: 8px !important;
  font-weight: 700 !important;
  padding: 10px 24px !important;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  font-size: 0.85rem !important;
  box-shadow: 0 2px 6px rgba(13,110,253,0.25) !important;
  transition: all .12s;
  cursor: pointer;
}
.cl-card button[type="submit"]:hover {
  filter: brightness(1.15);
  box-shadow: 0 4px 12px rgba(13,110,253,0.35) !important;
}

/* Cancel / secondary */
.cl-card a.cl-btn,
.cl-card button[type="button"],
.cl-card .btn-cancel {
  background: #fff !important;
  color: #1a3d7c !important;
  border: 2px solid #1a3d7c !important;
  border-radius: 8px !important;
  font-weight: 700 !important;
  padding: 10px 24px !important;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  font-size: 0.85rem !important;
  text-decoration: none !important;
  display: inline-block;
  transition: all .12s;
}
.cl-card a.cl-btn:hover,
.cl-card button[type="button"]:hover {
  background: #1a3d7c !important;
  color: #fff !important;
}
"""

if "Culture Labels action buttons" not in src:
    src = src + "\n" + css
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("button theme added")
else:
    print("already present")

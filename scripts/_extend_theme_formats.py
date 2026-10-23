"""Add tf-table + fp-ast to theme CSS."""
import io, os
path = os.path.join("static", "css", "test_settings_theme.css")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

additions = """
/* ===== formats + previews tables ===== */
table.tf-table, table.fp-ast {
  border-collapse: separate !important;
  border-spacing: 0 !important;
  border: 2px solid #212529 !important;
  border-radius: 12px !important;
  overflow: hidden !important;
}
table.tf-table thead th, table.fp-ast thead th {
  background: linear-gradient(135deg, #1a3d7c 0%, #0d6efd 100%) !important;
  color: #fff !important;
  padding: 10px 12px !important;
  text-transform: uppercase;
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.05em;
  border-right: 1px solid #212529 !important;
  border-bottom: 2px solid #212529 !important;
}
table.tf-table thead th:last-child, table.fp-ast thead th:last-child {
  border-right: none !important;
}
table.tf-table tbody td, table.fp-ast tbody td {
  padding: 8px 12px !important;
  border-bottom: 1px solid #212529 !important;
  border-right: 1px solid #212529 !important;
}
table.tf-table tbody td:last-child, table.fp-ast tbody td:last-child {
  border-right: none !important;
}
table.tf-table tbody tr:last-child td, table.fp-ast tbody tr:last-child td {
  border-bottom: none !important;
}
table.tf-table tbody tr:nth-child(even) td, table.fp-ast tbody tr:nth-child(even) td {
  background: #f7f9fc !important;
}
table.tf-table tbody tr:hover td, table.fp-ast tbody tr:hover td {
  background: #eaf2ff !important;
}
"""

if "table.tf-table" not in src:
    src = src + "\n" + additions
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("formats + previews classes added")
else:
    print("already added")

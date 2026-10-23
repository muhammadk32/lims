"""Force append fs-item borders CSS."""
import io, os
path = os.path.join("templates", "form_settings", "index.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== Bordered field items (FINAL) ===== */
.fs-item {
  border: 1.5px solid #212529 !important;
  border-radius: 6px !important;
  padding: 8px 12px !important;
  margin: 4px 0 !important;
  background: #fff !important;
  min-height: 42px !important;
  display: flex !important;
  align-items: center !important;
  gap: 10px !important;
}
.fs-item:hover {
  background: #f5f9ff !important;
  border-color: #0d6efd !important;
}
.fs-item label:not(.form-check-label),
.fs-item .name, .fs-item .lbl {
  font-weight: 700 !important;
  font-size: 0.85rem !important;
  text-transform: uppercase !important;
  letter-spacing: 0.02em !important;
  color: #212529 !important;
}
"""

# find last </style>
idx = src.rfind("</style>")
print("last </style> index:", idx)

if idx > 0:
    src = src[:idx] + add + src[idx:]
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("CSS appended")
else:
    print("no </style> found — dumping last 20 lines")
    print("\n".join(src.splitlines()[-20:]))

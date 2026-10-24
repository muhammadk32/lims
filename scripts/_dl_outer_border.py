"""Fix clipped outer border on .dl-summary."""
import io, os
path = os.path.join("modules", "orders", "templates", "orders", "list.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== FIX CLIPPED OUTER BORDER ===== */
.dl-summary {
    overflow: visible !important;
    border-radius: 8px !important;
    border: 2px solid #212529 !important;
}
.dl-summary .stat:first-child {
    border-top-left-radius: 6px !important;
    border-bottom-left-radius: 6px !important;
}
.dl-summary .stat:last-child {
    border-top-right-radius: 6px !important;
    border-bottom-right-radius: 6px !important;
}
"""

idx = src.rfind("</style>")
src = src[:idx] + add + src[idx:]
with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("Outer border fix applied.")

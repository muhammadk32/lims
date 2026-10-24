"""Center-align text in the footer summary."""
import io, os
path = os.path.join("modules", "orders", "templates", "orders", "list.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== CENTER FOOTER TEXT ===== */
.dl-summary .stat {
    align-items: center !important; /* Horizontally center */
    justify-content: center !important; /* Vertically center */
    text-align: center !important;
}
.dl-summary .label,
.dl-summary .value {
    text-align: center !important;
}
"""

idx = src.rfind("</style>")
if idx > 0:
    if "/* ===== CENTER FOOTER TEXT ===== */" not in src:
        src = src[:idx] + add + src[idx:]
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(src)
        print("Footer text centered.")

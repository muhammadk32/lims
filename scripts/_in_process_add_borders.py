"""Add dark borders to the header and search filter in in_process.html."""
import io, os
path = os.path.join("modules", "lab", "templates", "lab", "in_process.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== ADD DARK BORDERS TO HEADER AND FILTER ===== */
.tip-header {
    border: 2px solid #212529 !important;
}
.tip-filter {
    border: 2px solid #212529 !important;
}
"""

idx = src.rfind("</style>")
if idx > 0:
    if "/* ===== ADD DARK BORDERS TO HEADER AND FILTER ===== */" not in src:
        src = src[:idx] + add + src[idx:]
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(src)
        print("Borders added to header and filter.")
    else:
        print("Already applied.")

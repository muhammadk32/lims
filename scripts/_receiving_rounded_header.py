"""Round the top corners of the table header."""
import io, os
path = os.path.join("modules", "lab", "templates", "lab", "receiving.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== ROUND TOP CORNERS OF TABLE HEADER ===== */
.sr-table {
    border-collapse: separate !important; /* Required for border-radius to work */
    border-spacing: 0 !important;
    border-radius: 8px 8px 0 0 !important;
}

.sr-table thead th:first-child {
    border-top-left-radius: 8px !important;
}

.sr-table thead th:last-child {
    border-top-right-radius: 8px !important;
    border-right: none !important;
}
"""

idx = src.rfind("</style>")
if idx > 0:
    if "/* ===== ROUND TOP CORNERS OF TABLE HEADER ===== */" not in src:
        src = src[:idx] + add + src[idx:]
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(src)
        print("Rounded top corners applied to header.")
    else:
        print("Already applied.")

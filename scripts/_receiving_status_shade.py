"""Apply a soft background shade to the Status column."""
import io, os
path = os.path.join("modules", "lab", "templates", "lab", "receiving.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== STATUS COLUMN BACKGROUND SHADE ===== */
/* Target the 6th column (Status) td elements */
.sr-table tbody td:nth-child(6) {
    background-color: #fff8e1 !important; /* Soft amber shade */
    color: #212529 !important; /* Dark text */
}
"""

idx = src.rfind("</style>")
if idx > 0:
    if "/* ===== STATUS COLUMN BACKGROUND SHADE ===== */" not in src:
        src = src[:idx] + add + src[idx:]
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(src)
        print("Status column shade applied.")
    else:
        print("Already applied.")

"""Add dark borders to header and search filter area."""
import io, os
path = os.path.join("modules", "lab", "templates", "lab", "receiving.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== ADD DARK BORDERS TO HEADER AND FILTER ===== */

/* 1. Header Bar Border */
.sr-header {
    border: 2px solid #212529 !important; 
}

/* 2. Search Filter Box Border */
.sr-filter {
    border: 2px solid #212529 !important;
}

/* 3. Yellow Band Border */
.sr-band {
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

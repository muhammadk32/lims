"""Increase font size for the table body cells."""
import io, os
path = os.path.join("modules", "lab", "templates", "lab", "receiving.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== INCREASE TABLE BODY FONT ===== */
.sr-table tbody td {
    font-size: 1rem !important; /* Larger, readable size */
    padding: 12px 12px !important; /* Slight padding increase to breathe */
}
"""

idx = src.rfind("</style>")
if idx > 0:
    if "/* ===== INCREASE TABLE BODY FONT ===== */" not in src:
        src = src[:idx] + add + src[idx:]
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(src)
        print("Table body font increased.")
    else:
        print("Already applied.")

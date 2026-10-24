"""Color the Status column text (e.g., Sample To Come)."""
import io, os
path = os.path.join("modules", "lab", "templates", "lab", "receiving.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== STATUS COLUMN COLORING ===== */
/* Target the 6th column (Status) td elements */
.sr-table tbody td:nth-child(6) {
    color: #b58105 !important; /* Professional amber/orange color */
    font-weight: 800 !important; /* Bold */
    text-transform: uppercase !important; /* Make it look like a label */
    font-size: 0.85rem !important;
}
"""

idx = src.rfind("</style>")
if idx > 0:
    if "/* ===== STATUS COLUMN COLORING ===== */" not in src:
        src = src[:idx] + add + src[idx:]
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(src)
        print("Status column colored.")
    else:
        print("Already applied.")

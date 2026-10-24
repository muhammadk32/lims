"""Increase the max width of the receiving page."""
import io, os
path = os.path.join("modules", "lab", "templates", "lab", "receiving.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== PAGE WIDTH EXPANSION ===== */
.sr-page {
    max-width: 100% !important; /* Allow full width */
    padding: 16px 32px 40px !important; /* Slightly larger side padding */
}
"""

idx = src.rfind("</style>")
if idx > 0:
    if "/* ===== PAGE WIDTH EXPANSION ===== */" not in src:
        src = src[:idx] + add + src[idx:]
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(src)
        print("Page width expanded.")
    else:
        print("Already applied.")

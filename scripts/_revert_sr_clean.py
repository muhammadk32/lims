"""Undo the CLEAN SLATE style replacement only."""
import io, os
path = os.path.join("modules", "lab", "templates", "lab", "receiving.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

marker = "/* ===== CLEAN SLATE: MATCH REPORTS THEME EXACTLY ===== */"
if marker in src:
    start = src.find("<style>")
    end = src.find("</style>", start) + len("</style>")
    # replace with an empty style block
    src = src[:start] + "<style></style>" + src[end:]
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("Reverted the CLEAN SLATE block only.")
else:
    print("Marker not found; nothing to revert.")

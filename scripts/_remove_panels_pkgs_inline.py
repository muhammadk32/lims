"""Remove inline styles from panels + packages templates."""
import io, os
for p in ("_panels.html", "_packages.html"):
    path = os.path.join("templates", "test_settings", p)
    with io.open(path, "r", encoding="utf-8", newline="") as f:
        src = f.read()
    start = src.find("<style>")
    if start == 0:
        end = src.find("</style>") + len("</style>")
        nl_start = end
        while nl_start < len(src) and src[nl_start] in ('\r', '\n'):
            nl_start += 1
        src = src[nl_start:]
        print(f"{p}: inline style removed")
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(src)
    else:
        print(f"{p}: no inline style at start")

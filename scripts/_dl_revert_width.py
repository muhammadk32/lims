"""Revert the page width expansion for Daily Ledger."""
import io, os
path = os.path.join("modules", "orders", "templates", "orders", "list.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

marker = "/* ===== EXPAND PAGE WIDTH ===== */"
if marker in src:
    start = src.find(marker)
    end = src.find("</style>", start)
    src = src[:start] + src[end:]
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("Page width expansion removed.")
else:
    print("Marker not found.")

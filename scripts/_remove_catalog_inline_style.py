"""Remove inline theme overrides from _catalog.html — let global theme handle it."""
import io, os, re
path = os.path.join("templates", "test_settings", "_catalog.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

# Find and remove the injected <style> block at the very top
start = src.find("<style>")
if start == 0:
    end = src.find("</style>") + len("</style>")
    # preserve trailing newline
    nl_start = end
    while nl_start < len(src) and src[nl_start] in ('\r', '\n'):
        nl_start += 1
    removed = end - start
    src = src[nl_start:]
    print(f"removed {removed} chars of inline style")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

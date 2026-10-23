"""Remove bad head block, inject plain <style> instead."""
import io, os

BAD_BLOCK_START = "{% block head %}"
BAD_BLOCK_END = "{% endblock %}"

def fix(path):
    with io.open(path, "r", encoding="utf-8", newline="") as f:
        src = f.read()
    nl = "\r\n" if "\r\n" in src else "\n"

    # remove the entire {% block head %}...{% endblock %} block I injected
    start = src.find(BAD_BLOCK_START)
    if start == 0:
        end = src.find(BAD_BLOCK_END) + len(BAD_BLOCK_END) + len(nl)
        src = src[end:]
        print(f"{path}: removed head block")
    else:
        print(f"{path}: no head block at start")

    # prepend a plain <style> block
    style = (
"<style>" + nl +
".ts-table { border:2px solid #212529 !important; border-radius:10px; overflow:hidden; }" + nl +
".ts-table thead th { border-right:1px solid #444 !important; }" + nl +
".ts-table tbody td { border-bottom:1px solid #212529 !important; border-right:1px solid #212529 !important; }" + nl +
".ts-table tbody td:last-child { border-right:none !important; }" + nl +
".ts-table tbody tr:nth-child(even) td { background:#f7f9fc !important; }" + nl +
".ts-table tbody tr:hover td { background:#eaf2ff !important; }" + nl +
"</style>" + nl
    )
    if "<style>.ts-table { border:2px solid" not in src:
        src = style + src

    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)

for p in ("templates/test_settings/_panels.html",
          "templates/test_settings/_packages.html",
          "templates/test_settings/_catalog.html"):
    fix(p)

"""Darken panels + packages tables."""
import io, os

def darken(path):
    with io.open(path, "r", encoding="utf-8", newline="") as f:
        src = f.read()
    nl = "\r\n" if "\r\n" in src else "\n"

    # add dark borders to .ts-table
    if ".ts-table" in src and "border:2px solid #212529" not in src:
        # ensure style block exists
        if "<style>" not in src:
            style = (
"<style>" + nl +
".ts-table { width:100%; border-collapse:collapse; font-size:0.86rem; border:2px solid #212529; border-radius:10px; overflow:hidden; }" + nl +
".ts-table thead th { background:#212529; color:#fff; padding:8px 10px; text-align:left; text-transform:uppercase; font-size:0.78rem; border-right:1px solid #444; }" + nl +
".ts-table thead th:last-child { border-right:none; }" + nl +
".ts-table tbody td { padding:6px 10px; border-bottom:1px solid #212529; border-right:1px solid #212529; vertical-align:middle; }" + nl +
".ts-table tbody td:last-child { border-right:none; }" + nl +
".ts-table tbody tr:nth-child(even) td { background:#f7f9fc; }" + nl +
".ts-table tbody tr:hover td { background:#eaf2ff; }" + nl +
"</style>" + nl
            )
            src = style + src
        else:
            # append CSS block right after <style>
            css = (
nl +
".ts-table { border:2px solid #212529 !important; border-radius:10px; overflow:hidden; }" + nl +
".ts-table thead th { border-right:1px solid #444 !important; }" + nl +
".ts-table tbody td { border-bottom:1px solid #212529 !important; border-right:1px solid #212529 !important; }" + nl +
".ts-table tbody td:last-child { border-right:none !important; }" + nl +
".ts-table tbody tr:nth-child(even) td { background:#f7f9fc !important; }" + nl +
".ts-table tbody tr:hover td { background:#eaf2ff !important; }"
            )
            src = src.replace("<style>", "<style>" + css, 1)
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(src)
        return True
    return False

p1 = "templates/test_settings/_panels.html"
p2 = "templates/test_settings/_packages.html"

print(f"_panels.html: {darken(p1)}")
print(f"_packages.html: {darken(p2)}")

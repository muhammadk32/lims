"""Inject dark table CSS via head block."""
import io, os

CSS_BLOCK = """{% block head %}
{{ super() }}
<style>
.ts-table { border:2px solid #212529 !important; border-radius:10px; overflow:hidden; }
.ts-table thead th { border-right:1px solid #444 !important; }
.ts-table tbody td { border-bottom:1px solid #212529 !important; border-right:1px solid #212529 !important; }
.ts-table tbody td:last-child { border-right:none !important; }
.ts-table tbody tr:nth-child(even) td { background:#f7f9fc !important; }
.ts-table tbody tr:hover td { background:#eaf2ff !important; }
.ts-table .lt-badge { border-radius:0 !important; }
</style>
{% endblock %}
"""

def inject(path):
    with io.open(path, "r", encoding="utf-8", newline="") as f:
        src = f.read()
    nl = "\r\n" if "\r\n" in src else "\n"

    if ".ts-table { border:2px solid" in src:
        return False

    # insert CSS block at top of file
    src = CSS_BLOCK.replace("\n", nl) + src
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    return True

print(f"panels: {inject('templates/test_settings/_panels.html')}")
print(f"packages: {inject('templates/test_settings/_packages.html')}")
print(f"catalog: {inject('templates/test_settings/_catalog.html')}")

"""Add packages tab to shell.html."""
import io, os
path = os.path.join("templates", "test_settings", "shell.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

old = "    {% elif tab == 'panels' %}" + nl + "      {% include 'test_settings/_panels.html' %}"
new = (
"    {% elif tab == 'panels' %}" + nl +
"      {% include 'test_settings/_panels.html' %}" + nl +
"    {% elif tab == 'packages' %}" + nl +
"      {% include 'test_settings/_packages.html' %}"
)

if "test_settings/_packages.html" not in src:
    if old in src:
        src = src.replace(old, new, 1)
        print("packages dispatch added")
    else:
        print("ANCHOR MISS")
else:
    print("already present")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

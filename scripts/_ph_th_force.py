"""Force actions th width via inline style in template."""
import io, os
path = os.path.join("modules", "patients", "templates", "patients", "history.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

# replace any variant of the actions th
import re
src = re.sub(
    r'<th class="center" style="width: [^"]*">Actions</th>',
    '<th class="center actions-col" style="width: 280px !important; min-width: 280px !important;">Actions</th>',
    src
)

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("th forced to 280px")

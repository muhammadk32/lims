"""Embed window.LAB_RATE_MAP into orders/new.html."""
import io, os
path = os.path.join("modules", "orders", "templates", "orders", "new.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

if "LAB_RATE_MAP" not in src:
    anchor = "{% block content %}"
    inject = anchor + nl + "<script>window.LAB_RATE_MAP = {{ rate_map|default({})|tojson }};</script>"
    if anchor in src:
        src = src.replace(anchor, inject, 1)
        print("template: rate_map embedded")
    else:
        print("block content MISS")
else:
    print("already embedded")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

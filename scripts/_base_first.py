"""Force base.py first in pdf package."""
import io, os
path = os.path.join("modules", "reports", "pdf", "__init__.py")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

if "from . import base" not in src.split("generator")[0]:
    src = "from . import base  # noqa: F401 — installs Paragraph sanitizer BEFORE generator" + nl + src
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("base imported first")
else:
    print("already first")

Get-Content = None

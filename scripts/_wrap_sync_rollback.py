"""Wrap sync calls in try/rollback to prevent pending rollback errors."""
import io, os
path = os.path.join("modules", "settings", "routes.py")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

for tag in ("create", "edit"):
    old = (
"    try:" + nl +
"        from modules.laboratories.services import sync_lab_rate_list" + nl +
"        sync_lab_rate_list(lab)" + nl +
"    except Exception as _e:" + nl +
"        print(f'[lab-" + tag + "] rate list sync failed: {_e}')"
    )
    new = (
"    try:" + nl +
"        from modules.laboratories.services import sync_lab_rate_list" + nl +
"        sync_lab_rate_list(lab)" + nl +
"    except Exception as _e:" + nl +
"        db.session.rollback()" + nl +
"        print(f'[lab-" + tag + "] rate list sync failed: {_e}')"
    )
    if old in src:
        src = src.replace(old, new, 1)
        print(f"{tag} hook wrapped")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

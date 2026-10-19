"""Hook sync_lab_rate_list into lab_create + lab_edit."""
import io, os
path = os.path.join("modules", "settings", "routes.py")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

# after "db.session.add(lab); db.session.commit()" in create
old_create = "    db.session.add(lab)" + nl + "    db.session.commit()" + nl + "    flash(f'Laboratory \"{name}\" added.', 'success')"
new_create = (
"    db.session.add(lab)" + nl +
"    db.session.commit()" + nl +
"    try:" + nl +
"        from modules.laboratories.services import sync_lab_rate_list" + nl +
"        sync_lab_rate_list(lab)" + nl +
"    except Exception as _e:" + nl +
"        print(f'[lab-create] rate list sync failed: {_e}')" + nl +
"    flash(f'Laboratory \"{name}\" added.', 'success')"
)
if old_create in src:
    src = src.replace(old_create, new_create, 1)
    print("create hooked")
else:
    print("create anchor MISS")

# after edit's commit
old_edit = "    db.session.commit()" + nl + "    flash(f'Laboratory \"{lab.name}\" updated.', 'success')"
new_edit = (
"    db.session.commit()" + nl +
"    try:" + nl +
"        from modules.laboratories.services import sync_lab_rate_list" + nl +
"        sync_lab_rate_list(lab)" + nl +
"    except Exception as _e:" + nl +
"        print(f'[lab-edit] rate list sync failed: {_e}')" + nl +
"    flash(f'Laboratory \"{lab.name}\" updated.', 'success')"
)
if old_edit in src:
    src = src.replace(old_edit, new_edit, 1)
    print("edit hooked")
else:
    print("edit anchor MISS")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

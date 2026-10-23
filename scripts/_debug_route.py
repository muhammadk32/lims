"""Debug: print row keys before render."""
import io, os
path = os.path.join("modules", "tests", "routes.py")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

anchor = "    return render_template('test_settings/_rate_list_export.html', **ctx)"
debug = (
"    # DEBUG" + nl +
"    if rows:" + nl +
"        print('DEBUG first row keys:', list(rows[0].keys()))" + nl +
"        print('DEBUG first row:', rows[0])" + nl +
"    return render_template('test_settings/_rate_list_export.html', **ctx)"
)

if anchor in src and "DEBUG first row keys" not in src:
    src = src.replace(anchor, debug, 1)
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("debug print added")
else:
    print("already or anchor miss")

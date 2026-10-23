"""Add package dropdown to new_order route."""
import io, os
path = os.path.join("modules", "orders", "routes.py")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

old = "    return render_template(" + nl + "        'orders/new.html'," + nl + "        rate_map=build_lab_rate_map(),"
new = (
"    from modules.tests.models import Test" + nl +
"    packages = (Test.query" + nl +
"                .filter(Test.is_active == True," + nl +
"                        Test.result_format == 'package')" + nl +
"                .order_by(Test.name.asc()).all())" + nl +
nl +
"    return render_template(" + nl +
"        'orders/new.html'," + nl +
"        packages=packages," + nl +
"        rate_map=build_lab_rate_map(),"
)
if "packages=packages" not in src:
    src = src.replace(old, new, 1)
    print("route: packages passed")
else:
    print("already passed")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

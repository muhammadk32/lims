"""Split packages from panels."""
import io, os
path = os.path.join("modules", "tests", "routes.py")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

# 1) panels: exclude packages
old = (
"        q = request.args.get('q', '').strip()" + nl +
"        query = Test.query.filter(Test.is_active == True, Test.is_panel == True)  # noqa: E712" + nl +
"        if q:" + nl +
"            like = f'%{q}%'" + nl +
"            query = query.filter(or_(Test.code.ilike(like), Test.name.ilike(like)))" + nl +
"        panels = query.order_by(Test.name.asc()).all()"
)
new = (
"        q = request.args.get('q', '').strip()" + nl +
"        query = Test.query.filter(Test.is_active == True, Test.is_panel == True)  # noqa: E712" + nl +
"        query = query.filter((Test.result_format != 'package') | (Test.result_format.is_(None)))" + nl +
"        if q:" + nl +
"            like = f'%{q}%'" + nl +
"            query = query.filter(or_(Test.code.ilike(like), Test.name.ilike(like)))" + nl +
"        panels = query.order_by(Test.name.asc()).all()"
)
if old in src:
    src = src.replace(old, new, 1)
    print("panels excludes packages")

# 2) add new packages branch after panels branch closes
panels_end = "            'total_panels': len(panels)," + nl + "        })"
pkg_branch = (
"            'total_panels': len(panels)," + nl +
"        })" + nl +
nl +
"    elif tab == 'packages':" + nl +
"        from sqlalchemy import func" + nl +
"        q = request.args.get('q', '').strip()" + nl +
"        query = Test.query.filter(Test.is_active == True, Test.result_format == 'package')" + nl +
"        if q:" + nl +
"            like = f'%{q}%'" + nl +
"            query = query.filter(or_(Test.code.ilike(like), Test.name.ilike(like)))" + nl +
"        packages = query.order_by(Test.name.asc()).all()" + nl +
"        pkg_counts = dict(" + nl +
"            db.session.query(PanelParameter.panel_id, func.count(PanelParameter.id))" + nl +
"            .group_by(PanelParameter.panel_id).all()" + nl +
"        )" + nl +
"        ctx.update({" + nl +
"            'packages': packages," + nl +
"            'pkg_counts': pkg_counts," + nl +
"            'total_packages': len(packages)," + nl +
"        })"
)
if "elif tab == 'packages'" not in src:
    src = src.replace(panels_end, pkg_branch, 1)
    print("packages branch added")

# 3) add 'packages' to valid_tabs
src = src.replace(
"valid_tabs = ('catalog', 'formats', 'categories', 'panels', 'units', 'bulk', 'previews', 'rates')",
"valid_tabs = ('catalog', 'formats', 'categories', 'panels', 'packages', 'units', 'bulk', 'previews', 'rates')")
print("tab registered")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

"""Add /orders/api/test-children/<id> endpoint."""
import io, os
path = os.path.join("modules", "orders", "routes.py")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

if "/api/test-children/" not in src:
    route = (
nl + nl +
"@orders_bp.route('/api/test-children/<int:test_id>')" + nl +
"@login_required" + nl +
"def api_test_children(test_id):" + nl +
"    from modules.tests.models import Test, PanelParameter" + nl +
"    t = Test.query.get_or_404(test_id)" + nl +
"    children = []" + nl +
"    links = (PanelParameter.query" + nl +
"             .filter_by(panel_id=t.id)" + nl +
"             .order_by(PanelParameter.sort_order.asc()).all())" + nl +
"    for link in links:" + nl +
"        c = Test.query.get(link.test_id)" + nl +
"        if c:" + nl +
"            children.append({" + nl +
"                'id': c.id, 'code': c.code, 'name': c.name," + nl +
"                'price': float(c.price or 0)," + nl +
"            })" + nl +
"    return jsonify({" + nl +
"        'id': t.id, 'code': t.code, 'name': t.name," + nl +
"        'children': children," + nl +
"    })" + nl
    )
    src = src + route
    print("api endpoint added")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

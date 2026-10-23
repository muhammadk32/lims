"""Round all section headings, strips, cards on /orders/new."""
import io, os
path = os.path.join("modules", "orders", "templates", "orders", "new.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

if "/* ===== round corners global ===== */" not in src:
    css = (
"<style>" + nl +
"/* ===== round corners global ===== */" + nl +
"/* Section cells (patient, tests, billing, etc.) */" + nl +
".rec-cell { border-radius:12px !important; overflow:hidden; border:2px solid #212529 !important; }" + nl +
".rec-cell-title { border-radius:12px 12px 0 0 !important; padding:10px 14px !important; border-bottom:2px solid #212529 !important; }" + nl +
".rec-cell-body { padding:10px 12px !important; }" + nl +
"/* Tables inside cells */" + nl +
".rec-cell .basket-table { border-collapse:separate !important; border-spacing:0 !important; border:2px solid #212529 !important; border-radius:10px !important; overflow:hidden !important; }" + nl +
".rec-cell .basket-table thead th { border-right:1px solid #444 !important; }" + nl +
".rec-cell .basket-table thead th:last-child { border-right:none !important; }" + nl +
".rec-cell .basket-table tbody td { border-bottom:1px solid #212529 !important; border-right:1px solid #212529 !important; }" + nl +
".rec-cell .basket-table tbody td:last-child { border-right:none !important; }" + nl +
"/* Inputs / selects */" + nl +
".rec-cell .form-control, .rec-cell .form-select { border-radius:8px !important; }" + nl +
"/* Health package bar */" + nl +
"#packagePicker, #packagePicker option { border-radius:6px !important; }" + nl +
"/* Billing summary box */" + nl +
".billing-summary, .billing-box, .receipt-summary { border-radius:12px !important; }" + nl +
"/* Buttons */" + nl +
".rec-cell .btn { border-radius:8px !important; }" + nl +
"</style>" + nl
    )
    # inject right after {% block content %}
    anchor = "{% block content %}"
    if anchor in src:
        src = src.replace(anchor, anchor + nl + css, 1)
        print("round-corner CSS injected")
    else:
        print("block content MISS")
else:
    print("already injected")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

"""Align discount % block with other fields."""
import io, os
path = os.path.join("modules", "orders", "templates", "orders", "new.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

# 1) hide the hint block under the label
old_hint = (
"              <label for=\"discountPercentInput\">Discount %</label>" + nl +
"              <small class=\"text-info\" id=\"rateListHint\" style=\"display:none; font-size:0.7rem;\">" + nl +
"                <i class=\"bi bi-info-circle\"></i> Managed by lab rate list" + nl +
"              </small>"
)
new_hint = "              <label for=\"discountPercentInput\">Discount %</label>"
if old_hint in src:
    src = src.replace(old_hint, new_hint, 1)
    print("hint block removed from label row")
else:
    print("hint anchor MISS")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

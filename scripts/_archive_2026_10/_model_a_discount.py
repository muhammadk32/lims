"""Show gross subtotal + rate-list discount + net total (Model A)."""
import io, os
path = os.path.join("static", "js", "reception.js")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

# 1) add rateListDiscount after subtotal
old = (
"    const subtotal = state.selectedTests.reduce(" + nl +
"      (s, t) => s + (Number(t.price) || 0), 0" + nl +
"    );"
)
new = (
"    const subtotal = state.selectedTests.reduce(" + nl +
"      (s, t) => s + (Number(t.price) || 0), 0" + nl +
"    );" + nl +
"    const rateListDiscount = state.selectedTests.reduce(" + nl +
"      (s, t) => s + (Number(t.price) || 0) - (Number(t.company_rate != null ? t.company_rate : t.price) || 0), 0" + nl +
"    );"
)
if old in src and "rateListDiscount" not in src:
    src = src.replace(old, new, 1)
    print("rateListDiscount computed")
else:
    print("subtotal anchor MISS/already patched")

# 2) include in discountValue
old2 = "    let discountValue = roundMoney(cappedDiscount);"
new2 = "    let discountValue = roundMoney(cappedDiscount + rateListDiscount);"
if old2 in src:
    src = src.replace(old2, new2, 1)
    print("discount includes rateListDiscount")
else:
    print("discountValue anchor MISS/already patched")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

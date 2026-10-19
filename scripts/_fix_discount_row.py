"""Show rate-list discount in discountRow (remove d-none, set text)."""
import io, os
path = os.path.join("static", "js", "reception.js")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

old = (
"    if (roundedDiscount > 0) {" + nl +
"      $discountRow.style.display = 'flex';" + nl +
"      $sumDiscount.value = '−' + fmt(roundedDiscount);" + nl +
"    } else {" + nl +
"      $discountRow.style.display = 'none';" + nl +
"    }"
)
new = (
"    if (roundedDiscount > 0) {" + nl +
"      $discountRow.classList.remove('d-none');" + nl +
"      $discountRow.style.display = 'flex';" + nl +
"      $discountRow.style.fontSize = '0.85rem';" + nl +
"      $discountRow.style.color = '#dc3545';" + nl +
"      $discountRow.style.fontWeight = '600';" + nl +
"      $discountRow.style.padding = '4px 8px';" + nl +
"      $discountRow.textContent = 'Discount: −' + fmt(roundedDiscount);" + nl +
"      if ($sumDiscount) $sumDiscount.value = '−' + fmt(roundedDiscount);" + nl +
"    } else {" + nl +
"      $discountRow.classList.add('d-none');" + nl +
"      $discountRow.style.display = 'none';" + nl +
"    }"
)
if old in src:
    src = src.replace(old, new, 1)
    print("discount row display patched")
else:
    print("ANCHOR MISS")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

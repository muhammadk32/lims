"""Remove redundant bottom discount line; keep only the Discount Rs field."""
import io, os
path = os.path.join("static", "js", "reception.js")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

old = (
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
new = (
"    // bottom discount line removed — value shown in Discount Rs field" + nl +
"    if ($discountRow) { $discountRow.classList.add('d-none'); $discountRow.style.display = 'none'; }" + nl +
"    if ($sumDiscount) $sumDiscount.value = roundedDiscount > 0 ? ('−' + fmt(roundedDiscount)) : '0';"
)
if old in src:
    src = src.replace(old, new, 1)
    print("bottom line removed")
else:
    print("anchor MISS")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

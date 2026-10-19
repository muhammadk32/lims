"""Mirror computed discount into the Discount Rs field when a rate list is active."""
import io, os
path = os.path.join("static", "js", "reception.js")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

# expose _labHasRateList globally
anchor1 = (
"  function _labHasRateList() {" + nl +
"    var labId = (document.getElementById('laboratoryId') || {}).value;" + nl +
"    if (!labId) return false;" + nl +
"    var m = (window.LAB_RATE_MAP || {})[labId];" + nl +
"    return !!m && Object.keys(m).length > 0;" + nl +
"  }"
)
if anchor1 in src and "window._labHasRateList" not in src:
    src = src.replace(anchor1, anchor1 + nl + "  window._labHasRateList = _labHasRateList;", 1)
    print("exposed globally")

# mirror value into discountAmount field
anchor2 = "    const roundedDiscount = discountValue;"
add2 = anchor2 + nl + "    if (window._labHasRateList && window._labHasRateList() && $discountAmount) {" + nl + "      $discountAmount.value = roundedDiscount.toFixed(2);" + nl + "    }"
if anchor2 in src and "Mirror computed discount" not in src and "$discountAmount.value = roundedDiscount" not in src:
    src = src.replace(anchor2, add2, 1)
    print("mirror inserted")
else:
    print("mirror already or anchor missing")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

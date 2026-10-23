"""Fix package picker: set search input instead of calling addTest."""
import io, os
path = os.path.join("modules", "orders", "templates", "orders", "new.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

# replace existing __onPackagePick function body
old_start = src.find("window.__onPackagePick = function(pkgId) {")
if old_start >= 0:
    old_end = src.find("};", old_start) + 2
    new_fn = (
"window.__onPackagePick = function(pkgId) {" + nl +
"  if (!pkgId) return;" + nl +
"  var sel = document.getElementById('packagePicker');" + nl +
"  var opt = sel.options[sel.selectedIndex];" + nl +
"  if (!opt) return;" + nl +
"  var pkgName = opt.dataset.name;" + nl +
"  var pkgCode = opt.dataset.code;" + nl +
"  // type the package name into the search box and trigger search" + nl +
"  var searchInput = document.getElementById('testSearch');" + nl +
"  if (searchInput) {" + nl +
"    searchInput.value = pkgName;" + nl +
"    searchInput.dispatchEvent(new Event('input', { bubbles: true }));" + nl +
"    searchInput.focus();" + nl +
"  }" + nl +
"  sel.selectedIndex = 0;" + nl +
"};"
    )
    src = src[:old_start] + new_fn + src[old_end:]
    print("package picker → sets search input")
else:
    print("anchor MISS")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

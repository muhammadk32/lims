"""Fix package picker: fire input event + trigger search reliably."""
import io, os
path = os.path.join("modules", "orders", "templates", "orders", "new.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

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
"  var searchInput = document.getElementById('testSearch');" + nl +
"  if (searchInput) {" + nl +
"    searchInput.value = pkgName;" + nl +
"    searchInput.dispatchEvent(new Event('input', { bubbles: true }));" + nl +
"    searchInput.dispatchEvent(new Event('change', { bubbles: true }));" + nl +
"    searchInput.dispatchEvent(new KeyboardEvent('keyup', { bubbles: true, key: 'a' }));" + nl +
"    searchInput.focus();" + nl +
"    // Give the search debounce a moment, then check results" + nl +
"    setTimeout(function() {" + nl +
"      var results = document.getElementById('testSearchResults');" + nl +
"      if (results && results.style.display !== 'none' && results.children.length > 0) {" + nl +
"        var firstResult = results.querySelector('.test-search-result, [data-test-id]');" + nl +
"        if (firstResult) { firstResult.click(); }" + nl +
"      } else {" + nl +
"        console.warn('[pkg-pick] search returned no results for', pkgName);" + nl +
"      }" + nl +
"    }, 400);" + nl +
"  }" + nl +
"  sel.selectedIndex = 0;" + nl +
"};"
    )
    src = src[:old_start] + new_fn + src[old_end:]
    print("package picker → auto-click first result")
else:
    print("anchor MISS")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

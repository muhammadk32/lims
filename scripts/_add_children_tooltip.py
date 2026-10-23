"""Add children tooltip to basket rows (via title attribute)."""
import io, os
path = os.path.join("static", "js", "reception.js")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

# 1) Preload children map for all selected tests (batch fetch)
# Add a global cache + fetch function
if "__childrenCache" not in src:
    cache_init = (
nl +
"  // ===== Children tooltip cache =====" + nl +
"  var __childrenCache = {};" + nl +
"  function __fetchChildren(testId) {" + nl +
"    if (__childrenCache[testId]) return Promise.resolve(__childrenCache[testId]);" + nl +
"    return fetch('/orders/api/test-children/' + testId)" + nl +
"      .then(function(r){ return r.json(); })" + nl +
"      .then(function(data){" + nl +
"        __childrenCache[testId] = data;" + nl +
"        return data;" + nl +
"      })" + nl +
"      .catch(function(){ return {children: []}; });" + nl +
"  }" + nl +
"  window.__fetchChildren = __fetchChildren;" + nl
    )
    # insert inside the IIFE, right after "const $testSearch = ..." area
    anchor = "  const $testSearch = document.getElementById('testSearch');"
    if anchor in src:
        src = src.replace(anchor, anchor + cache_init, 1)
        print("children cache added")

# 2) In renderSelectedTests, after building each row, set title asynchronously
old_add_remove = "    body.querySelectorAll('.si-remove').forEach(btn => {"
if "__attachChildrenTooltips" not in src:
    tooltip_helper = (
"    // attach children tooltips" + nl +
"    state.selectedTests.forEach((t, idx) => {" + nl +
"      if (!t.is_panel && !t.parameter_count) return;" + nl +
"      var tr = body.querySelectorAll('tr')[idx];" + nl +
"      if (!tr) return;" + nl +
"      __fetchChildren(t.id).then(function(data){" + nl +
"        if (!data || !data.children || !data.children.length) {" + nl +
"          tr.title = '(no children)';" + nl +
"          return;" + nl +
"        }" + nl +
"        var lines = ['Children of ' + data.name + ':'];" + nl +
"        data.children.forEach(function(c){" + nl +
"          lines.push('  ' + c.code + ' — ' + c.name + ' (Rs ' + c.price + ')');" + nl +
"        });" + nl +
"        tr.title = lines.join('\\n');" + nl +
"        tr.style.cursor = 'help';" + nl +
"      });" + nl +
"    });" + nl +
nl +
old_add_remove
    )
    src = src.replace(old_add_remove, tooltip_helper, 1)
    print("tooltip attach added")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

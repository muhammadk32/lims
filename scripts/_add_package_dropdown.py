"""Add package dropdown above test search in new.html."""
import io, os
path = os.path.join("modules", "orders", "templates", "orders", "new.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

# Insert above the search input — find the search box
anchor = '<input type="text" id="testSearchInput"'
if anchor not in src:
    # try alt id
    anchor = 'id="testSearch"'

# Insert dropdown BEFORE the tests & panels table
# Find the <table or div that holds the test rows — safer: insert after the search form
# Look for 'Type name or code'
anchor2 = 'Type name or code...'

insert_point = src.find(anchor2)
if insert_point > 0:
    # find start of the containing form/div block
    block_start = src.rfind('<div', 0, insert_point)
    block_start = src.rfind('<div', 0, block_start)  # go one level up
    
    pkg_dropdown = (
'<div style="background:#f0f4ff; border:2px solid #212529; border-radius:8px; padding:10px 14px; margin:10px 0; display:flex; align-items:center; gap:12px;">' + nl +
'  <label style="font-weight:700; font-size:0.82rem; text-transform:uppercase; color:#495057; margin:0;">' + nl +
'    <i class="bi bi-box-seam"></i> Health Package' + nl +
'  </label>' + nl +
'  <select id="packagePicker" class="form-select form-select-sm" style="max-width:320px;" onchange="if(this.value){const q=this.options[this.selectedIndex].text; document.getElementById(\'testSearchInput\') ? (document.getElementById(\'testSearchInput\').value=q) : null; this.selectedIndex=0; if(typeof window.__onPackagePick===\'function\') window.__onPackagePick(this.value);}">' + nl +
'    <option value="">— Select a package —</option>' + nl +
'    {% for pkg in packages %}' + nl +
'    <option value="{{ pkg.id }}">{{ pkg.name }}</option>' + nl +
'    {% endfor %}' + nl +
'  </select>' + nl +
'  <small class="text-muted" style="font-size:0.78rem;">Or search by name below</small>' + nl +
'</div>' + nl
    )
    src = src[:block_start] + pkg_dropdown + src[block_start:]
    print("package dropdown inserted")
else:
    print("anchor for search box not found")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

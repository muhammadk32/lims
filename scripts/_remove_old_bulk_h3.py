"""Remove the old duplicate h3+subtitle block (from initial bulk template)."""
import io, os
path = os.path.join("templates", "test_settings", "_bulk.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

# Find the old h3 that says "Bulk Import — Tests & Panels" WITHOUT .bi-hero wrapper
# (i.e., the one from the original bulk-card)
old_block = """  <h3><i class="bi bi-upload"></i> Bulk Import — Tests &amp; Panels</h3>
  <div class="bulk-sub">Import multiple tests/panels from CSV. Duplicates (same code) will be updated, not duplicated.</div>"""

if old_block in src:
    src = src.replace(old_block, '', 1)
    print("old h3+subtitle removed")
else:
    # try without &amp;
    old_block2 = old_block.replace("&amp;", "&")
    if old_block2 in src:
        src = src.replace(old_block2, '', 1)
        print("old h3+subtitle removed (v2)")
    else:
        print("old block not found — dump 40-60 lines")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

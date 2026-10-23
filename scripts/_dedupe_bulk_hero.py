"""Remove duplicate hero section."""
import io, os
path = os.path.join("templates", "test_settings", "_bulk.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

hero = (
'<div class="bi-hero">' + nl +
'  <div class="icon"><i class="bi bi-cloud-upload"></i></div>' + nl +
'  <div>' + nl +
'    <h3>Bulk Import — Tests &amp; Panels</h3>' + nl +
'    <p>Import multiple tests from CSV. Duplicates (same code) are updated, not duplicated.</p>' + nl +
'  </div>' + nl +
'</div>'
)

# Count occurrences
count = src.count(hero)
print(f"hero occurrences: {count}")

if count > 1:
    # Remove all but the first
    first = src.find(hero)
    head = src[:first + len(hero)]
    tail = src[first + len(hero):]
    tail = tail.replace(hero + nl, '', 1)
    tail = tail.replace(hero, '', 1)
    src = head + tail
    print("duplicate hero removed")
elif count == 1:
    # Hero might be the OLD one too (different tag) — check for duplicate bulk-card
    pass

# Also check for duplicate "Bulk Import — Tests & Panels" plain heading (from old bulk-card h3)
import re
old_h3_matches = re.findall(r'<h3[^>]*>.*?Bulk Import.*?</h3>', src, flags=re.DOTALL)
print(f"h3 'Bulk Import' occurrences: {len(old_h3_matches)}")

# If more than 1 h3 → remove the extra nested h3/subtitle/desc block after hero
if len(old_h3_matches) > 1:
    # Remove second h3 + its subtitle in old bulk-card
    pattern = (
        r'(<div class="bi-hero">.*?</div>' + re.escape(nl) + r'\s*</div>' + re.escape(nl) + r'\s*</div>' + re.escape(nl) + r')'
        r'(?:.*?)'
        r'(<h3[^>]*>Bulk Import.*?</h3>.*?<div class="bulk-sub"[^>]*>.*?</div>)'
    )
    # simpler: find second h3, remove the h3 + bulk-sub that follows
    matches = list(re.finditer(r'<h3[^>]*>\s*<i[^>]*></i>\s*Bulk Import[^<]*</h3>', src))
    if len(matches) > 1:
        # find the block from the 2nd h3 through end of next bulk-sub div
        second = matches[1]
        block_start = second.start()
        # find the </div> closing the .bulk-sub
        sub_start = src.find('<div class="bulk-sub"', block_start)
        if sub_start > 0:
            sub_end = src.find('</div>', sub_start) + len('</div>')
            src = src[:block_start] + src[sub_end:]
            print("duplicate h3+subtitle removed")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

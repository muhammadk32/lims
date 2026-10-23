"""Force dark borders via regex — all border rules in rle-table."""
import io, os, re
path = os.path.join("templates", "test_settings", "_rate_list_export.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

# 1) Outer table border: replace any border:Npx solid X within .rle-table {...}
src = re.sub(
    r'(\.rle-table\s*\{[^}]*?)border:\s*\d+px\s+solid\s+[^;!]+(?!\s*!important)',
    r'\1border:2px solid #212529 !important',
    src,
    count=1,
    flags=re.DOTALL
)

# 2) All border-right/border-bottom in table cells → dark
src = re.sub(
    r'border-right:\s*\d+px\s+solid\s+(?!\#212529)[^;!]+',
    'border-right:1px solid #212529 !important',
    src
)
src = re.sub(
    r'border-bottom:\s*\d+px\s+solid\s+(?!\#212529)[^;!]+',
    'border-bottom:1px solid #212529 !important',
    src
)

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("regex replaced all border rules")

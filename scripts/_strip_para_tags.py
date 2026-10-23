"""Extend sanitizer: also strip <para> wrappers."""
import io, os
path = os.path.join("modules", "reports", "pdf", "base.py")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

# Add <para> handling at end of _sanitize_para_global before "return s"
old = "    # bare br not inside p (rare)"
new = (
"    # strip stray <para>...</para> (reportlab doesn't understand these, treats as unclosed)" + "\r\n" +
"    s = _re.sub(r'</?para[^>]*>', '', s, flags=_re.I)" + "\r\n" +
"    # bare br not inside p (rare)"
)
if old in src and "strip stray <para>" not in src:
    src = src.replace(old, new, 1)
    print("para tag stripper added")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

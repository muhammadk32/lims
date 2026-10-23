"""Sanitize HTML before Paragraph() — remove empty paragraphs and stray <br>."""
import io, os

SANITIZER = '''

def _sanitize_para(html):
    """Clean up HTML fragments that break reportlab's paragraph parser.

    - Removes <p> with only <br> inside
    - Strips trailing <br> before closing </p>
    - Collapses multiple consecutive <br> to one
    """
    if not html:
        return ''
    import re
    s = str(html)
    # empty <p>...</p> with only whitespace or brs
    s = re.sub(r'<p>\\s*(?:<br\\s*/?>\\s*)*</p>', '', s, flags=re.I)
    # brs before </p>
    s = re.sub(r'(?:<br\\s*/?>\\s*)+</p>', '</p>', s, flags=re.I)
    # brs right after <p>
    s = re.sub(r'<p>\\s*(?:<br\\s*/?>\\s*)+', '<p>', s, flags=re.I)
    # collapse runs
    s = re.sub(r'(?:<br\\s*/?>\\s*){3,}', '<br/>', s, flags=re.I)
    return s.strip()
'''

# 1) Add sanitizer to results_table.py
path = os.path.join("modules", "reports", "pdf", "results_table.py")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

if "_sanitize_para" not in src:
    # insert helper after imports
    first_def = src.find("\ndef ")
    if first_def < 0:
        src = src + SANITIZER.replace("\n", nl)
    else:
        src = src[:first_def] + SANITIZER.replace("\n", nl) + src[first_def:]
    print("sanitizer added to results_table.py")

# 2) Wrap _pick() results with sanitizer
# _pick returns the html/text. Wrap the .Paragraph() call sites.
# Simplest: change _pick's return to sanitize.
old_pick_start = "def _pick("
idx = src.find(old_pick_start)
if idx >= 0:
    # find end of function body (next \ndef or \ndefn at column 0)
    body_start = src.find(":", idx) + 1
    body_end = src.find(nl + "def ", body_start)
    if body_end < 0: body_end = len(src)
    old_body = src[body_start:body_end]
    if "return _sanitize_para(" not in old_body:
        # patch return lines inside _pick to wrap with sanitizer
        new_body = old_body.replace("return val", "return _sanitize_para(val)")
        new_body = new_body.replace("return x", "return _sanitize_para(x)")
        new_body = new_body.replace("return v", "return _sanitize_para(v)")
        src = src[:body_start] + new_body + src[body_end:]
        print("_pick wrapped with sanitizer")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

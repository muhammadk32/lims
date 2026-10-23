"""Global Paragraph sanitizer: patch reportlab to clean html before parsing."""
import io, os
path = os.path.join("modules", "reports", "pdf", "base.py")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

if "_sanitize_para_global" not in src:
    patch = (
nl +
"import re as _re" + nl +
"from reportlab.platypus import Paragraph as _RLParagraph" + nl +
nl +
"def _sanitize_para_global(html):" + nl +
"    if not html:" + nl +
"        return html" + nl +
"    s = str(html)" + nl +
"    # empty <p> with only brs/whitespace → remove" + nl +
"    s = _re.sub(r'<p>\\s*(?:<br\\s*/?>\\s*)*</p>', '', s, flags=_re.I)" + nl +
"    # trailing brs before </p>" + nl +
"    s = _re.sub(r'(?:<br\\s*/?>\\s*)+</p>', '</p>', s, flags=_re.I)" + nl +
"    # leading brs after <p>" + nl +
"    s = _re.sub(r'<p>\\s*(?:<br\\s*/?>\\s*)+', '<p>', s, flags=_re.I)" + nl +
"    # collapse 3+ brs to one" + nl +
"    s = _re.sub(r'(?:<br\\s*/?>\\s*){3,}', '<br/>', s, flags=_re.I)" + nl +
"    # bare br not inside p (rare)" + nl +
"    s = _re.sub(r'<br\\s*/?>', '<br/>', s, flags=_re.I)" + nl +
"    return s" + nl +
nl +
"_orig_rl_paragraph_init = _RLParagraph.__init__" + nl +
"def _patched_paragraph_init(self, text, style, *args, **kwargs):" + nl +
"    if isinstance(text, str):" + nl +
"        text = _sanitize_para_global(text)" + nl +
"    return _orig_rl_paragraph_init(self, text, style, *args, **kwargs)" + nl +
"_RLParagraph.__init__ = _patched_paragraph_init" + nl +
"print('[pdf-base] paragraph sanitizer installed')" + nl
    )
    src = src + patch
    print("patch appended to base.py")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

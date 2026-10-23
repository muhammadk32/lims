"""Strip ALL HTML from _rrfo output — range text is display only."""
import io, os
path = os.path.join("modules", "reports", "pdf", "base.py")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

# add a stronger stripper inside _sanitize_para_global
old = "    # strip stray <para>...</para>"
new = (
"    # FULL html strip — range/notes text is display-only; no styling needed" + "\r\n" +
"    import re as _r2" + "\r\n" +
"    # preserve a handful of allowed tags" + "\r\n" +
"    _allowed = ('b','i','u','br','sub','sup','font')" + "\r\n" +
"    def _strip_bad(m):" + "\r\n" +
"        t = m.group(1).lower().split()[0].strip('/')" + "\r\n" +
"        return m.group(0) if t in _allowed else ''" + "\r\n" +
"    s = _r2.sub(r'<([a-zA-Z][^>]*)>', _strip_bad, s)" + "\r\n" +
"    # now close/balance and strip stray <para>" + "\r\n" +
"    # strip stray <para>...</para>"
)
if "FULL html strip" not in src:
    src = src.replace(old, new, 1)
    print("full strip added")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

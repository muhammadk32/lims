"""Sanitize _rrfo output at Paragraph call."""
import io, os
path = os.path.join("modules", "reports", "pdf", "results_table.py")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

old = "                        Paragraph('' if child_is_pcr else (_rrfo(child.test, order) or '-'), cell_style),"
new = "                        Paragraph('' if child_is_pcr else _sanitize_para(_rrfo(child.test, order) or '-'), cell_style),"

if old in src:
    src = src.replace(old, new, 1)
    print("line 385 sanitized")
else:
    print("anchor miss")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

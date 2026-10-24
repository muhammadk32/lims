"""Delete ALL .dl-summary blocks and append one final blue gradient block."""
import io, os, re
path = os.path.join("modules", "orders", "templates", "orders", "list.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

# Use regex to find every block that starts with .dl-summary or .dl-summary .stat etc.
# Safer: iterate lines and drop any block referencing .dl-summary OR [data-bs-theme="dark"] .dl-summary
lines = src.splitlines(keepends=True)
out = []
i = 0
removed = 0
while i < len(lines):
    line = lines[i]
    if line.lstrip().startswith(".dl-summary") or line.lstrip().startswith("[data-bs-theme=\"dark\"] .dl-summary"):
        # Determine full selector — could span multiple lines (comma-separated).
        # Walk forward until we hit a line ending with "{" for this group, then consume to matching "}".
        depth = 0
        started = False
        j = i
        while j < len(lines):
            depth += lines[j].count("{") - lines[j].count("}")
            if "{" in lines[j]:
                started = True
            if started and depth <= 0:
                j += 1
                break
            j += 1
        # Drop lines i..j-1
        i = j
        removed += 1
        continue
    out.append(line)
    i += 1

src = "".join(out)

# Also remove stale comments and empty spacing
src = re.sub(r"/\* ===== .*?FOOTER.*?===== \*/\n", "", src)

# Append the final blue block
final_block = """
/* ===== FINAL FOOTER (BLUE GRADIENT) ===== */
.dl-summary {
    display: grid !important;
    grid-template-columns: repeat(6, 1fr) !important;
    gap: 0 !important;
    margin-top: 16px !important;
    border: 2px solid #212529 !important;
    border-radius: 8px !important;
    overflow: hidden !important;
    background: linear-gradient(180deg, #0d6efd 0%, #1a3d7c 100%) !important;
}
.dl-summary .stat {
    padding: 14px 16px !important;
    border-right: 1px solid #212529 !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 4px !important;
    box-sizing: border-box !important;
    background: transparent !important;
}
.dl-summary .stat:last-child { border-right: none !important; }

.dl-summary .label {
    font-family: 'Segoe UI', Arial, sans-serif !important;
    font-size: 0.72rem !important;
    font-weight: 800 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
    color: #fff !important;
    opacity: 0.9 !important;
    margin: 0 !important;
}
.dl-summary .value {
    font-family: 'Segoe UI', Arial, sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 800 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
    color: #fff !important;
    margin: 0 !important;
}
"""

# Insert before the LAST </style>
idx = src.rfind("</style>")
src = src[:idx] + final_block + src[idx:]

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print(f"Removed {removed} .dl-summary blocks. Final blue footer added.")

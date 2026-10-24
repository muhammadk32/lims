"""Apply blue gradient footer with white text matching table header."""
import io, os
path = os.path.join("modules", "orders", "templates", "orders", "list.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== FOOTER = BLUE GRADIENT HEADER STYLE ===== */
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
    padding: 12px 16px !important;
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
}
.dl-summary .value {
    font-family: 'Segoe UI', Arial, sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 800 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
    color: #fff !important;
}
"""

idx = src.rfind("</style>")
src = src[:idx] + add + src[idx:]
with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("Footer converted to blue gradient header style.")

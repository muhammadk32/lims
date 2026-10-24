"""Append one final clean .dl-summary block."""
import io, os
path = os.path.join("modules", "orders", "templates", "orders", "list.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== FINAL SUMMARY (guaranteed) ===== */
.dl-summary {
    display: grid !important;
    grid-template-columns: repeat(6, 1fr) !important;
    gap: 0 !important;
    margin-top: 16px !important;
    border: 2px solid #212529 !important;
    border-radius: 8px !important;
    overflow: hidden !important;
    background: #fff !important;
}
.dl-summary .stat {
    padding: 14px 16px !important;
    border-right: 1px solid #212529 !important;
    border-bottom: none !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 4px !important;
    box-sizing: border-box !important;
}
.dl-summary .stat:last-child { border-right: none !important; }

.dl-summary .stat:nth-child(1) { background: #f0f7ff !important; }
.dl-summary .stat:nth-child(2) { background: #fef2f2 !important; }
.dl-summary .stat:nth-child(3) { background: #f0fdf4 !important; }
.dl-summary .stat:nth-child(4) { background: #f8f9fa !important; }
.dl-summary .stat:nth-child(5) { background: #fef2f2 !important; }
.dl-summary .stat:nth-child(6) { background: #fff8e1 !important; }

.dl-summary .label {
    font-size: 0.72rem !important;
    font-weight: 800 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    color: #6c757d !important;
}
.dl-summary .value {
    font-size: 1rem !important;
    font-weight: 800 !important;
    font-family: Consolas, Monaco, monospace !important;
}
.dl-summary .stat:nth-child(1) .value { color: #1a3d7c !important; }
.dl-summary .stat:nth-child(2) .value { color: #b02a37 !important; }
.dl-summary .stat:nth-child(3) .value { color: #146c43 !important; }
.dl-summary .stat:nth-child(4) .value { color: #212529 !important; }
.dl-summary .stat:nth-child(5) .value { color: #b02a37 !important; }
.dl-summary .stat:nth-child(6) .value { color: #664d03 !important; }
"""
idx = src.rfind("</style>")
src = src[:idx] + add + src[idx:]
with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("Final block appended.")

"""Equalize the lv-left and lv-right panel widths."""
import io, os
path = os.path.join("modules", "lab", "templates", "lab", "verify.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== EQUALIZE PANELS 50/50 ===== */
.lv-page {
    display: flex !important;
    flex-direction: row !important;
    gap: 20px !important;
    align-items: flex-start !important;
    box-sizing: border-box !important;
}
.lv-left {
    flex: 1 1 50% !important;
    max-width: 50% !important;
    min-width: 0 !important;
}
.lv-right {
    flex: 1 1 50% !important;
    max-width: 50% !important;
    min-width: 0 !important;
    box-sizing: border-box !important;
    height: fit-content !important;
}
.lv-right > *,
.lv-right .panel,
.lv-right .card {
    width: 100% !important;
    box-sizing: border-box !important;
}
/* Ensure filters stretch but don't overflow */
.lv-filter-row {
    grid-template-columns: 1.5fr 1fr 1fr auto !important;
}
"""

idx = src.rfind("</style>")
if idx > 0:
    if "/* ===== EQUALIZE PANELS 50/50 ===== */" not in src:
        src = src[:idx] + add + src[idx:]
        with io.open(path, "w", encoding="utf-8", newline="") as f:
            f.write(src)
        print("Left/right panels equalized.")
    else:
        print("Already applied.")

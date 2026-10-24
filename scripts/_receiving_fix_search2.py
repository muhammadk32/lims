"""Fix search bar to match exact Reports style (rounded, clean grid)."""
import io, os
path = os.path.join("modules", "lab", "templates", "lab", "receiving.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== STRICT SEARCH BAR FIX ===== */
.sr-filter {
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    gap: 10px !important;
    background: #fff !important; /* White background */
    border: 1px solid #dee2e6 !important; /* Light grey border */
    border-radius: 8px !important; /* Round corners */
    padding: 16px !important;
    margin-bottom: 16px !important;
    box-sizing: border-box !important;
    width: 100% !important;
}

/* Force hide any weird labels */
.sr-filter::before, .sr-filter::after {
    display: none !important;
    content: none !important;
}

.sr-filter input {
    flex: 0 0 auto !important;
    width: 350px !important; /* Fixed width for input */
    height: 38px !important;
    padding: 8px 12px !important;
    border: 1px solid #ced4da !important;
    border-radius: 4px !important;
    font-size: 0.9rem !important;
    background: #fff !important;
    box-shadow: none !important;
    margin: 0 !important;
}

.sr-filter .sr-btn {
    height: 38px !important;
    padding: 0 20px !important;
    background: #198754 !important;
    color: #fff !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    border-radius: 4px !important;
    border: 1px solid #198754 !important;
    text-transform: uppercase !important;
    margin: 0 !important;
    cursor: pointer !important;
}
"""

idx = src.rfind("</style>")
if idx > 0:
    # Remove previous bad block if exists
    if "/* ===== REFINED SEARCH BAR & TABLE BOX ===== */" in src:
        start = src.find("/* ===== REFINED SEARCH BAR & TABLE BOX ===== */")
        src = src[:start] + add + src[idx:]
    elif "/* ===== STRICT SEARCH BAR FIX ===== */" not in src:
        src = src[:idx] + add + src[idx:]

    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("Search bar strictly styled with round corners.")

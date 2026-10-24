"""Fix search bar layout and table dark border."""
import io, os
path = os.path.join("modules", "lab", "templates", "lab", "receiving.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* ===== REFINED SEARCH BAR & TABLE BOX ===== */

/* 1. Clean up the Search Box container */
.sr-filter {
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    gap: 12px !important;
    background: #f8f9fa !important; /* Light grey like Reports */
    border: 1px solid #dee2e6 !important;
    border-radius: 6px !important;
    padding: 12px 16px !important;
    margin-bottom: 16px !important;
}

/* Remove the ugly "SEARCH" text prefix */
.sr-filter::before {
    content: none !important;
    display: none !important;
}

/* Make the input compact */
.sr-filter input {
    width: 320px !important;
    max-width: 100% !important;
    height: 36px !important;
    padding: 6px 12px !important;
    border: 1px solid #ced4da !important;
    border-radius: 4px !important;
    background: #fff !important;
    box-shadow: none !important;
}

/* The Search button */
.sr-filter .sr-btn {
    height: 36px !important;
    padding: 0 16px !important;
    background: #198754 !important;
    color: #fff !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    border-radius: 4px !important;
    border: 1px solid #198754 !important;
    text-transform: uppercase !important;
}

/* 2. Ensure table container has a thick black border all the way around */
.sr-card {
    border: 2px solid #212529 !important;
    border-radius: 6px !important;
    overflow: hidden !important;
}
.sr-table {
    border: none !important; /* Let the card handle the outer border */
}
"""

idx = src.rfind("</style>")
if idx > 0:
    # Remove old conflicting fixes
    if "/* ===== REFINED SEARCH BAR & TABLE BOX ===== */" in src:
        start = src.find("/* ===== REFINED SEARCH BAR & TABLE BOX ===== */")
        src = src[:start] + add + src[idx:]
    else:
        src = src[:idx] + add + src[idx:]

    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("Search bar and table borders refined.")

"""Fix topnav dropdown styling using correct .topnav-dropdown class."""
import io, os
path = os.path.join("templates", "layout", "topnav.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

# Remove the old broken block
if "/* ===== Professional Dropdown Menu ===== */" in src:
    start = src.find("<style>\n/* ===== Professional Dropdown Menu ===== */")
    end = src.find("</style>", start) + 8
    if start != -1 and end != -1:
        src = src[:start] + src[end:]

css = """
<style>
/* ===== PROFESSIONAL TOPNAV DROPDOWNS ===== */
.topnav-item .topnav-dropdown {
    background: #fff !important;
    border: 1px solid #dee2e6 !important;
    border-radius: 8px !important;
    box-shadow: 0 10px 30px rgba(0,0,0,0.15) !important;
    padding: 8px 0 !important;
    margin-top: 4px !important;
    min-width: 230px !important;
    z-index: 1000;
}
.topnav-item .dropdown-section {
    font-size: 0.72rem !important;
    font-weight: 800 !important;
    color: #1a3d7c !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    padding: 10px 20px 4px 20px !important;
    margin-top: 4px;
}
.topnav-item .dropdown-divider {
    border-top: 1px solid #e9ecef !important;
    margin: 8px 0 !important;
}
.topnav-item .dropdown-item {
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    color: #212529 !important;
    padding: 9px 20px !important;
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
    text-decoration: none !important;
    transition: all 0.15s ease-in-out !important;
    border-left: 3px solid transparent !important;
}
.topnav-item .dropdown-item i {
    font-size: 1.05rem !important;
    color: #6c757d !important;
    transition: color 0.15s ease !important;
}
.topnav-item .dropdown-item:hover,
.topnav-item .dropdown-item.active {
    background: #f0f7ff !important;
    color: #1a3d7c !important;
    border-left-color: #1a3d7c !important;
}
.topnav-item .dropdown-item:hover i,
.topnav-item .dropdown-item.active i {
    color: #1a3d7c !important;
}
</style>
"""

idx = src.rfind("</body>")
if idx == -1: idx = src.rfind("</html>")
if idx > 0:
    src = src[:idx] + css + src[idx:]
else:
    src += css

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("Corrected dropdown CSS applied.")

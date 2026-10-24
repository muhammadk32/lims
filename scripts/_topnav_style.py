"""Style the Laboratory dropdown menu professionally."""
import io, os
path = os.path.join("templates", "layout", "topnav.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

css = """
<style>
/* ===== Professional Dropdown Menu ===== */
.topnav-item .dropdown-menu {
    border: 1px solid #dee2e6 !important;
    border-radius: 8px !important;
    box-shadow: 0 10px 25px rgba(0,0,0,0.1) !important;
    padding: 8px 0 !important;
    margin-top: 8px !important;
    background-color: #fff !important;
    min-width: 220px !important;
}
.topnav-item .dropdown-item {
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    color: #495057 !important;
    padding: 10px 20px !important;
    transition: all 0.2s ease !important;
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
}
.topnav-item .dropdown-item i {
    font-size: 1.1rem !important;
    color: #6c757d !important;
    transition: color 0.2s ease !important;
}
.topnav-item .dropdown-item:hover, 
.topnav-item .dropdown-item.active {
    background-color: #f0f7ff !important;
    color: #1a3d7c !important;
    border-left: 3px solid #1a3d7c !important;
    padding-left: 17px !important; /* offset the 3px border */
}
.topnav-item .dropdown-item:hover i,
.topnav-item .dropdown-item.active i {
    color: #1a3d7c !important;
}
</style>
"""

if "Professional Dropdown Menu" not in src:
    idx = src.rfind("</body>")
    if idx == -1:
        idx = src.rfind("</html>")
    if idx > 0:
        src = src[:idx] + css + src[idx:]
    else:
        src += css
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("Dropdown CSS added to topnav.html")
else:
    print("Already applied")

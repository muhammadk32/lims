"""Professional restyle of bulk import page."""
import io, os
path = os.path.join("templates", "test_settings", "_bulk.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

new_css = (
"<style>" + nl +
".bi-hero {" + nl +
"  background:linear-gradient(135deg,#1a3d7c 0%,#0d6efd 100%);" + nl +
"  color:#fff; border-radius:14px; padding:18px 24px;" + nl +
"  margin-bottom:18px; box-shadow:0 4px 12px rgba(0,0,0,0.15);" + nl +
"  display:flex; align-items:center; gap:14px;" + nl +
"}" + nl +
".bi-hero .icon { font-size:2rem; opacity:0.9; }" + nl +
".bi-hero h3 { margin:0; font-size:1.2rem; font-weight:800; letter-spacing:0.02em; }" + nl +
".bi-hero p { margin:2px 0 0; font-size:0.85rem; opacity:0.9; }" + nl +
"" + nl +
".bi-steps {" + nl +
"  display:grid; grid-template-columns:repeat(3,1fr); gap:14px;" + nl +
"  margin-bottom:20px;" + nl +
"}" + nl +
".bi-step {" + nl +
"  background:#fff; border:2px solid #1a3d7c; border-radius:12px;" + nl +
"  padding:16px 18px; position:relative;" + nl +
"  box-shadow:0 2px 6px rgba(0,0,0,0.06);" + nl +
"  transition:transform .15s, box-shadow .15s;" + nl +
"}" + nl +
".bi-step:hover { transform:translateY(-2px); box-shadow:0 4px 12px rgba(0,0,0,0.12); }" + nl +
".bi-step .num {" + nl +
"  position:absolute; top:-12px; left:16px;" + nl +
"  width:32px; height:32px; border-radius:50%;" + nl +
"  background:linear-gradient(135deg,#ffd166 0%,#ffb703 100%);" + nl +
"  color:#1a1a1a; font-weight:800; font-size:0.95rem;" + nl +
"  display:flex; align-items:center; justify-content:center;" + nl +
"  box-shadow:0 2px 6px rgba(0,0,0,0.2);" + nl +
"}" + nl +
".bi-step .label {" + nl +
"  font-weight:800; font-size:0.9rem; text-transform:uppercase;" + nl +
"  color:#1a3d7c; letter-spacing:0.04em; margin-top:8px;" + nl +
"}" + nl +
".bi-step .desc {" + nl +
"  font-size:0.8rem; color:#6c757d; margin-top:6px; line-height:1.4;" + nl +
"}" + nl +
"" + nl +
".bi-actions {" + nl +
"  display:flex; gap:10px; flex-wrap:wrap; margin-bottom:18px;" + nl +
"}" + nl +
".bi-btn {" + nl +
"  display:inline-flex; align-items:center; gap:8px;" + nl +
"  padding:10px 20px; border:2px solid #1a3d7c; border-radius:8px;" + nl +
"  background:#fff; color:#1a3d7c; font-weight:700; font-size:0.85rem;" + nl +
"  cursor:pointer; text-decoration:none; transition:all .12s;" + nl +
"}" + nl +
".bi-btn:hover { background:#1a3d7c; color:#fff; }" + nl +
".bi-btn-primary {" + nl +
"  background:linear-gradient(135deg,#1a3d7c 0%,#0d6efd 100%);" + nl +
"  color:#fff; border-color:#1a3d7c;" + nl +
"}" + nl +
".bi-btn-primary:hover { filter:brightness(1.15); color:#fff; }" + nl +
"" + nl +
".bi-info {" + nl +
"  background:linear-gradient(135deg,#fff8e1 0%,#fff3cd 100%);" + nl +
"  border-left:5px solid #ffc107; border-radius:8px;" + nl +
"  padding:14px 18px; margin-bottom:18px;" + nl +
"  font-size:0.85rem; color:#664d03;" + nl +
"}" + nl +
".bi-info strong { color:#664d03; font-weight:800; }" + nl +
".bi-info code {" + nl +
"  background:#fff; padding:2px 6px; border-radius:4px;" + nl +
"  border:1px solid #ffc107; font-size:0.78rem;" + nl +
"}" + nl +
".bi-info ul { margin:6px 0 0 18px; padding:0; }" + nl +
".bi-info li { margin-bottom:3px; }" + nl +
"" + nl +
".bi-upload {" + nl +
"  border:2.5px dashed #adb5bd; border-radius:12px;" + nl +
"  padding:26px 20px; text-align:center; background:#f8f9fa;" + nl +
"  margin-bottom:16px; cursor:pointer; transition:all .15s;" + nl +
"}" + nl +
".bi-upload:hover { border-color:#0d6efd; background:#f0f4ff; }" + nl +
".bi-upload.dragover { background:#e7f1ff; border-color:#0d6efd; border-style:solid; }" + nl +
".bi-upload input[type=\"file\"] { display:none; }" + nl +
".bi-upload .icon { font-size:2.2rem; color:#1a3d7c; }" + nl +
".bi-upload .main-text { font-weight:700; color:#1a3d7c; margin:8px 0 4px; font-size:0.95rem; }" + nl +
".bi-upload .sub-text { font-size:0.8rem; color:#6c757d; }" + nl +
"" + nl +
".bi-footer {" + nl +
"  display:flex; justify-content:flex-end; gap:10px;" + nl +
"  padding-top:14px; border-top:1px dashed #adb5bd;" + nl +
"}" + nl +
"</style>"
)

# replace the whole <style>...</style>
start = src.find("<style>")
end = src.find("</style>") + len("</style>")
if start >= 0:
    src = src[:start] + new_css + src[end:]
    print("styles replaced")

# now restyle the body — replace the .bulk-card opening wrapper
src = src.replace(
'<div class="bulk-card">',
'<div class="bi-hero">' + nl +
'  <div class="icon"><i class="bi bi-cloud-upload"></i></div>' + nl +
'  <div>' + nl +
'    <h3>Bulk Import — Tests &amp; Panels</h3>' + nl +
'    <p>Import multiple tests from CSV. Duplicates (same code) are updated, not duplicated.</p>' + nl +
'  </div>' + nl +
'</div>' + nl +
'' + nl +
'<div class="bulk-card" style="background:transparent; border:none; padding:0; box-shadow:none;">'
)

# swap class names to new ones
src = src.replace('class="bulk-steps"', 'class="bi-steps"')
src = src.replace('class="bulk-step"', 'class="bi-step"')
src = src.replace('class="bulk-actions"', 'class="bi-actions"')
src = src.replace('class="bulk-btn bulk-btn-primary"', 'class="bi-btn bi-btn-primary"')
src = src.replace('class="bulk-btn"', 'class="bi-btn"')
src = src.replace('class="bulk-info"', 'class="bi-info"')
src = src.replace('class="bulk-upload" id="dropzone"', 'class="bi-upload" id="dropzone"')

# update inner step markers to new classes
src = src.replace('<div class="n">', '<div class="num">')

# rename inner upload divs
src = src.replace(
'<div style="font-size:2rem; color:#1a3d7c;"><i class="bi bi-cloud-arrow-up"></i></div>',
'<div class="icon"><i class="bi bi-cloud-arrow-up"></i></div>')
src = src.replace(
'<div style="font-weight:700; margin:8px 0 4px;">Drop CSV here or click to select</div>',
'<div class="main-text">Drop CSV here or click to select</div>')
src = src.replace(
'<div style="font-size:0.8rem; color:#6c757d;" id="fileName">No file selected</div>',
'<div class="sub-text" id="fileName">No file selected</div>')

# footer wrapper
src = src.replace(
'<div style="display:flex; gap:10px; justify-content:flex-end;">',
'<div class="bi-footer">')

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("body restyled")

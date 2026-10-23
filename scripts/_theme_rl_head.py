"""Theme rate list page header + filter."""
import io, os
path = os.path.join("static", "css", "test_settings_theme.css")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

css = """
/* ===== Rate list tab: page header ===== */
.rl-head {
  background: linear-gradient(135deg, #1a3d7c 0%, #0d6efd 100%) !important;
  color: #fff !important;
  padding: 14px 20px !important;
  border-radius: 12px !important;
  border: 2px solid #1a3d7c !important;
  margin-bottom: 14px !important;
  box-shadow: 0 4px 12px rgba(0,0,0,0.12) !important;
  display: flex; align-items: center; justify-content: space-between;
}
.rl-head h2,
.rl-head h2 strong,
.rl-head h2 i {
  color: #fff !important;
}
.rl-head h2 i { color: #ffd166 !important; }

/* The Add button keeps its normal look */
.rl-head .btn-primary {
  color: #fff !important;
}

/* Filter strip already covered by .rl-filter, ensure it's consistent */
.rl-filter {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%) !important;
  border: 2px solid #1a3d7c !important;
  border-radius: 12px !important;
}

/* Also target any h2 sitting directly in .rl-page that says "MASTER RATE LIST" */
.rl-page > h2,
.rl-page > .rl-head h2 {
  color: #fff !important;
}

/* Wrap any plain h2 in rl-page that's not already inside rl-head */
.rl-page > h2 {
  background: linear-gradient(135deg, #1a3d7c 0%, #0d6efd 100%);
  padding: 14px 20px;
  border-radius: 12px;
  border: 2px solid #1a3d7c;
  margin: 0 0 14px 0;
  box-shadow: 0 4px 12px rgba(0,0,0,0.12);
}
.rl-page > h2 i {
  color: #ffd166 !important;
}
"""

if ".rl-head {" not in src:
    src = src + "\n" + css
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("rate list header theme added")
else:
    print("already present")

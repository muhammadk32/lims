"""Prevent flex shrink on action buttons."""
import io, os
path = os.path.join("modules", "patients", "templates", "patients", "history.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

add = """
/* Prevent action buttons from shrinking */
.ph-icon-btn {
  flex-shrink: 0 !important;
  flex-grow: 0 !important;
}
.ph-row-actions {
  min-width: max-content !important;
}
"""

idx = src.rfind("</style>")
if "Prevent action buttons from shrinking" not in src:
    src = src[:idx] + add + src[idx:]
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("flex-shrink prevented")

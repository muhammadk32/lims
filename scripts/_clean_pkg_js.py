"""Strip orphan code after __onPackagePick."""
import io, os
path = os.path.join("modules", "orders", "templates", "orders", "new.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

# Find the script that contains __onPackagePick
start_marker = "window.__onPackagePick = function(pkgId) {"
start = src.find(start_marker)
if start < 0:
    print("start not found")
else:
    # Find the closing </script> for this block
    script_end = src.find("</script>", start)
    if script_end < 0:
        print("script end not found")
    else:
        # Inside this script block, find the last complete "};" that closes __onPackagePick
        # We know the function starts at 'start', find "  sel.selectedIndex = 0;" then "};" right after
        anchor_close = "  sel.selectedIndex = 0;" + nl + "};"
        close_pos = src.find(anchor_close, start)
        if close_pos < 0:
            print("function close not found")
        else:
            close_end = close_pos + len(anchor_close)
            # Everything from close_end to script_end is garbage — replace
            clean = (
src[:close_end] + nl + "</script>"
            )
            src = clean + src[script_end + len("</script>"):]
            print("garbage removed")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

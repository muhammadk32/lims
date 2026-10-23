"""Expose addTest + state to window for package picker."""
import io, os
path = os.path.join("static", "js", "reception.js")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

if "window.addTest" not in src:
    # find the addTest function end and add exposures after
    anchor = "  function addTest(t) {"
    idx = src.find(anchor)
    if idx < 0:
        print("addTest anchor not found")
    else:
        # find the closing brace of the function: next "\r\n  }\r\n" after idx
        end = src.find(nl + "  }" + nl, idx)
        if end < 0:
            print("end of addTest not found")
        else:
            end += len(nl + "  }" + nl)
            inject = (
                "  window.addTest = addTest;" + nl +
                "  window.state = state;" + nl +
                "  window.renderSelectedTests = renderSelectedTests;" + nl +
                "  window.updateBilling = updateBilling;" + nl
            )
            src = src[:end] + inject + src[end:]
            print("exposed addTest + helpers")
else:
    print("already exposed")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

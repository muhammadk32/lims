"""Move topnav style block from end of body to inside <head>."""
import io, os
path = os.path.join("templates", "layout", "topnav.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

marker = "<style>\n/* ===== PROFESSIONAL TOPNAV DROPDOWNS ===== */"
if marker in src:
    start = src.find(marker)
    end = src.find("</style>", start) + len("</style>")
    block = src[start:end]
    src = src[:start] + src[end:]
    # insert right after </head> or <body> if no head here
    if "</head>" in src:
        src = src.replace("</head>", block + "\n</head>", 1)
    elif "<body" in src:
        # put it right after <body ...>
        i = src.find(">", src.find("<body")) + 1
        src = src[:i] + block + src[i:]
    else:
        src = block + src
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("Moved style block into head.")
else:
    print("Block not found.")

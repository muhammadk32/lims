"""Direct style injection into antibiotics page header to force button + badge layout."""
import io, os
path = os.path.join("templates", "settings", "antibiotics.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

override = (
"/* === FORCE FIX: actions + status === */" + nl +
".admin-content table td:last-child { white-space: nowrap !important; text-align: center !important; vertical-align: middle !important; padding: 4px 6px !important; min-width: 220px !important; }" + nl +
".admin-content table td:last-child > * { display: inline-flex !important; margin: 0 3px !important; vertical-align: middle !important; }" + nl +
".admin-content table td:last-child form { display: inline-flex !important; margin: 0 !important; padding: 0 !important; }" + nl +
".admin-content table td:last-child form button { display: inline-flex !important; }" + nl +
".admin-content table td:last-child a, .admin-content table td:last-child button {" + nl +
"  height: 32px !important; min-height: 32px !important; padding: 0 12px !important; min-width: 32px !important;" + nl +
"  font-size: 0.75rem !important; font-weight: 700 !important; letter-spacing: 0.03em !important; text-transform: uppercase !important;" + nl +
"  border-radius: 8px !important; border: 2px solid !important; align-items: center !important; justify-content: center !important;" + nl +
"  line-height: 1 !important; box-sizing: border-box !important; white-space: nowrap !important; text-decoration: none !important;" + nl +
"}" + nl +
".admin-content table td:last-child button:has(>i:only-child), .admin-content table td:last-child a:has(>i:only-child) { width: 32px !important; padding: 0 !important; }" + nl +
".admin-content table td:last-child i { font-size: 0.9rem !important; }" + nl +
"/* Status pill */" + nl +
".admin-content table td .badge, .admin-content table td .pill, .admin-content table td [class*='status'] {" + nl +
"  display: inline-block !important; padding: 6px 16px !important; font-size: 0.78rem !important; font-weight: 800 !important;" + nl +
"  border-radius: 6px !important; letter-spacing: 0.05em !important; text-transform: uppercase !important; line-height: 1.15 !important;" + nl +
"}" + nl +
".admin-content table td .badge.bg-success, .admin-content table td .status-active {" + nl +
"  background: #198754 !important; color: #fff !important; border: 2px solid #0f5132 !important;" + nl +
"}" + nl +
"/* Bigger body text */" + nl +
".admin-content table tbody td { font-size: 0.95rem !important; padding: 10px 12px !important; }" + nl +
".admin-content table thead th { font-size: 0.82rem !important; padding: 12px 12px !important; }" + nl
)

# find </style> in the page
idx = src.find("</style>")
if idx > 0:
    src = src[:idx] + override + src[idx:]
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("override injected into antibiotics.html")
else:
    print("no </style> in template")

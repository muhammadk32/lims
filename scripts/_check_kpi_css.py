import io, os
path = os.path.join("static", "css", "test_settings_theme.css")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

# find ALL occurrences of ".ts-kpi"
import re
matches = [(m.start(), src[max(0,m.start()-20):m.start()+200]) for m in re.finditer(r'\.ts-kpi\s*\{', src)]
print(f"occurrences: {len(matches)}")
for i, (pos, snippet) in enumerate(matches):
    print(f"\n--- occurrence {i+1} at {pos} ---")
    print(snippet[:200])

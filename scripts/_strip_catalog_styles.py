"""Strip ALL <style> blocks from catalog (leave body intact)."""
import io, os, re
path = os.path.join("templates", "test_settings", "_catalog.html")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()

# Remove all <style>...</style> blocks
new_src = re.sub(r'<style>.*?</style>\s*', '', src, flags=re.DOTALL)
if new_src != src:
    print(f"removed {len(src) - len(new_src)} chars")
    src = new_src
else:
    print("no <style> found")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

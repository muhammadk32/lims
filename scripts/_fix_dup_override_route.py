"""Remove duplicate rate_test_save_override definitions (keep last)."""
import io, os
path = os.path.join("modules", "tests", "routes.py")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

pattern = (
"@tests_bp.route('/rate-lists/<int:cat_id>/test-override/<int:test_id>', methods=['POST'])" + nl +
"@login_required" + nl +
"@permission_required('manage_tests')" + nl +
"def rate_test_save_override(cat_id, test_id):"
)
count = src.count(pattern)
print(f"occurrences: {count}")

if count > 1:
    parts = src.split(pattern)
    head = parts[0]
    keep_last = pattern + parts[-1]
    src = head + keep_last
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("kept last only")
else:
    print("no dup")

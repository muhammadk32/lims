"""Apply type_filter in catalog branch."""
import io, os
path = os.path.join("modules", "tests", "routes.py")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

# Find the catalog branch and add type_filter logic
old = (
"        type_filter = request.args.get('type_filter', '').strip()" + nl +
"        specimen_id = request.args.get('specimen', type=int)" + nl +
nl +
"        query = Test.query"
)
new = (
"        type_filter = request.args.get('type_filter', '').strip()" + nl +
"        type_choice = request.args.get('type', 'tests').strip()" + nl +
"        specimen_id = request.args.get('specimen', type=int)" + nl +
nl +
"        query = Test.query" + nl +
"        # Type filter: default hides **-prefixed parameter rows" + nl +
"        if type_choice == 'tests':" + nl +
"            query = query.filter(~Test.name.like('**%'))" + nl +
"        elif type_choice == 'parameters':" + nl +
"            query = query.filter(Test.name.like('**%'))"
)
if "type_choice = request.args.get('type'" not in src and old in src:
    src = src.replace(old, new, 1)
    print("type_choice logic added")

# Also pass type_filter to template context so dropdown remembers selection
old_ctx = (
"            'type_filter': type_filter," + nl +
"            'specimen_id': specimen_id,"
)
new_ctx = (
"            'type_filter': type_filter," + nl +
"            'specimen_id': specimen_id," + nl +
"            'type_choice': type_choice,"
)
# The template uses "type_filter" as var name; rename to avoid collision
# Simplest: pass the value as 'type_filter' in the query param sense — but
# template checks {% if type_filter == 'parameters' %}.
# Better: shadow type_filter with type_choice for the template.
if "'type_choice': type_choice" not in src and old_ctx in src:
    src = src.replace(old_ctx, new_ctx, 1)
    print("type_choice passed to context")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

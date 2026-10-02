# Add current_user import to tests/routes.py
p = 'modules/tests/routes.py'
s = open(p, encoding='utf-8').read()

# Check what's imported
if 'from flask_login import' in s:
    # Add current_user if missing
    import re
    match = re.search(r'from flask_login import ([^\n]+)', s)
    if match:
        imports = match.group(1)
        if 'current_user' not in imports:
            new_imports = imports.rstrip() + ', current_user'
            s = s.replace(
                f'from flask_login import {imports}',
                f'from flask_login import {new_imports}',
                1,
            )
            open(p, 'w', encoding='utf-8').write(s)
            print('OK - current_user added to flask_login import')
        else:
            print('SKIP - current_user already imported')
else:
    # No flask_login import — add one
    lines = s.split('\n')
    # Insert after the last 'from flask import' line
    for i, line in enumerate(lines):
        if line.startswith('from flask import') or line.startswith('from flask '):
            lines.insert(i + 1, 'from flask_login import login_required, current_user')
            break
    s = '\n'.join(lines)
    open(p, 'w', encoding='utf-8').write(s)
    print('OK - flask_login import added')

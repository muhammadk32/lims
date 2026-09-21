"""
One-time fix: add the `theme` column to the `users` table.
Safe to run multiple times — it checks if the column exists first.
"""
import os
import sqlite3
import sys

# ---- Locate the SQLite database ----
CANDIDATES = [
    'database.db',
    os.path.join('instance', 'database.db'),
    os.path.join('instance', 'lab_management_system.db'),
]

db_path = None
for path in CANDIDATES:
    if os.path.exists(path):
        db_path = path
        break

if not db_path:
    print('❌ Could not find database file. Looked in:')
    for p in CANDIDATES:
        print('   -', p)
    print('\nEdit the CANDIDATES list above with the correct path.')
    sys.exit(1)

print(f'✓ Found database: {db_path}')

# ---- Connect and check current columns ----
con = sqlite3.connect(db_path)
cur = con.cursor()
cur.execute('PRAGMA table_info(users)')
columns = [row[1] for row in cur.fetchall()]

if 'theme' in columns:
    print('✓ Column "theme" already exists — nothing to do.')
    con.close()
    sys.exit(0)

print('→ Adding column "theme"...')

# ---- Add the column ----
# SQLite requires the DEFAULT for NOT NULL columns being added to existing rows
cur.execute(
    "ALTER TABLE users ADD COLUMN theme VARCHAR(30) NOT NULL DEFAULT 'light'"
)
con.commit()

# ---- Verify ----
cur.execute('PRAGMA table_info(users)')
columns = [row[1] for row in cur.fetchall()]
if 'theme' in columns:
    print('✅ Column added successfully!')
else:
    print('❌ Something went wrong — column not found after ALTER TABLE.')
    con.close()
    sys.exit(1)

con.close()

# ---- Tell Alembic to skip this migration ----
print()
print('→ Marking Alembic revision as applied...')
exit_code = os.system('flask db stamp head')
if exit_code != 0:
    print('⚠️  Warning: "flask db stamp head" failed.')
    print('   Run it manually after this script:')
    print('   > flask db stamp head')

print()
print('=' * 50)
print('  DONE — You can now start the app:')
print('  > python app.py')
print('=' * 50)
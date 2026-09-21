"""
Diagnostic + fix for LabMS panel fields.

Targets the real database at instance/database.db.
Runs diagnostics first, then applies the fix if needed.
"""
import sqlite3
import sys
from pathlib import Path

DB = Path('instance') / 'database.db'

if not DB.exists():
    print(f'❌ Not found: {DB.resolve()}')
    sys.exit(1)

print('=' * 60)
print(f'  Database: {DB.resolve()}')
print(f'  Size:     {DB.stat().st_size:,} bytes')
print('=' * 60)
print()

con = sqlite3.connect(str(DB))
cur = con.cursor()

# ============================================================
# DIAGNOSTICS
# ============================================================
print('--- DIAGNOSTICS ---')
print()

# Tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [r[0] for r in cur.fetchall()]
print('Tables in DB:')
for t in tables:
    print(f'  • {t}')
print()

# Alembic version
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alembic_version'")
if cur.fetchone():
    cur.execute("SELECT version_num FROM alembic_version")
    rows = cur.fetchall()
    print(f'Alembic version: {rows}')
else:
    print('Alembic version: (no alembic_version table)')
print()

# Tests columns
cur.execute('PRAGMA table_info(tests)')
test_cols = [r[1] for r in cur.fetchall()]
print('Columns in `tests`:')
for c in test_cols:
    print(f'  • {c}')
print()

# Check what we need
needs = []
for col in ('result_format', 'is_panel', 'sort_order'):
    if col not in test_cols:
        needs.append(col)

has_panel_params = 'panel_parameters' in tables

print('Missing pieces:')
if needs:
    for c in needs:
        print(f'  ✗ Column: tests.{c}')
else:
    print('  ✓ All 3 columns already exist')
if not has_panel_params:
    print('  ✗ Table: panel_parameters')
else:
    print('  ✓ Table: panel_parameters exists')
print()

# ============================================================
# APPLY FIX (only if needed)
# ============================================================
if not needs and has_panel_params:
    print('✅ Nothing to do — DB is up to date.')
    con.close()
    sys.exit(0)

print('--- APPLYING FIX ---')
print()

for col_name, col_type, default in [
    ('result_format', 'VARCHAR(20)', "'numeric'"),
    ('is_panel',      'BOOLEAN',     '0'),
    ('sort_order',    'INTEGER',     '0'),
]:
    if col_name in test_cols:
        continue
    sql = f'ALTER TABLE tests ADD COLUMN {col_name} {col_type} NOT NULL DEFAULT {default}'
    print(f'→ {sql}')
    cur.execute(sql)

if not has_panel_params:
    print('→ CREATE TABLE panel_parameters ...')
    cur.execute('''
        CREATE TABLE panel_parameters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            panel_id INTEGER NOT NULL,
            test_id INTEGER NOT NULL,
            sort_order INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (panel_id) REFERENCES tests (id) ON DELETE CASCADE,
            FOREIGN KEY (test_id)  REFERENCES tests (id) ON DELETE CASCADE,
            UNIQUE (panel_id, test_id)
        )
    ''')
    cur.execute('CREATE INDEX ix_panel_parameters_panel_id ON panel_parameters (panel_id)')
    cur.execute('CREATE INDEX ix_panel_parameters_test_id ON panel_parameters (test_id)')
    print('  ✓ Created with indexes')

con.commit()

# ============================================================
# VERIFY
# ============================================================
print()
print('--- VERIFICATION ---')
print()

cur.execute('PRAGMA table_info(tests)')
cols = [r[1] for r in cur.fetchall()]
print('tests columns (new ones marked ✓):')
for c in cols:
    marker = '✓' if c in ('result_format', 'is_panel', 'sort_order') else ' '
    print(f'  [{marker}] {c}')
print()

cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='panel_parameters'")
print(f'panel_parameters exists: {bool(cur.fetchone())}')
print()

con.close()

print('=' * 60)
print('✅ DONE')
print()
print('Next:')
print('  1.  flask db stamp head')
print('  2.  python app.py')
print('=' * 60)
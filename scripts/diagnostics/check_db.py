"""Quick DB schema check."""
import sqlite3
from pathlib import Path

DB = Path('instance') / 'database.db'

if not DB.exists():
    print(f'❌ Not found: {DB.resolve()}')
    raise SystemExit(1)

print(f'✓ Database: {DB.resolve()}')
print(f'  Size: {DB.stat().st_size:,} bytes')
print()

con = sqlite3.connect(str(DB))
cur = con.cursor()

# ---- tests ----
print('=== tests columns ===')
cur.execute('PRAGMA table_info(tests)')
test_cols = [r[1] for r in cur.fetchall()]
for c in test_cols:
    marker = '  ✅' if c in ('result_format', 'is_panel', 'sort_order') else '   '
    print(f'{marker} {c}')
print()

# ---- order_items ----
print('=== order_items columns ===')
cur.execute('PRAGMA table_info(order_items)')
oi_cols = [r[1] for r in cur.fetchall()]
for c in oi_cols:
    marker = '  ✅' if c in ('parent_item_id', 'sort_order') else '   '
    print(f'{marker} {c}')
print()

# ---- panel_parameters table ----
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='panel_parameters'")
has_pp = bool(cur.fetchone())
print(f'=== panel_parameters table: {"✅ EXISTS" if has_pp else "❌ MISSING"} ===')
print()

# ---- Summary / action items ----
missing_in_oi = [c for c in ('parent_item_id', 'sort_order') if c not in oi_cols]

if missing_in_oi:
    print('🔧 Missing columns in order_items:', ', '.join(missing_in_oi))
    print('   Adding them now...')
    for c in missing_in_oi:
        if c == 'parent_item_id':
            cur.execute('ALTER TABLE order_items ADD COLUMN parent_item_id INTEGER')
        elif c == 'sort_order':
            cur.execute('ALTER TABLE order_items ADD COLUMN sort_order INTEGER NOT NULL DEFAULT 0')
        print(f'   ✓ Added {c}')
    try:
        cur.execute('CREATE INDEX ix_order_items_parent_item_id ON order_items (parent_item_id)')
        print('   ✓ Index created')
    except sqlite3.OperationalError:
        print('   ✓ Index already exists')
    con.commit()

    # Re-print
    print()
    print('=== order_items columns (after fix) ===')
    cur.execute('PRAGMA table_info(order_items)')
    for r in cur.fetchall():
        print('  ', r[1])
else:
    print('✅ All required columns exist. Ready to test.')

con.close()
print()
print('Done.')
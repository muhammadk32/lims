import sqlite3
c = sqlite3.connect("instance/database.db")

# Get ids
std = c.execute("select id from rate_categories where name='Standard Rate List'").fetchone()[0]
lmn = c.execute("select id from rate_categories where name='LMN rate'").fetchone()[0]
print(f"Standard id={std}, LMN id={lmn}")

std_ids = {r[0] for r in c.execute("select test_id from rate_category_tests where rate_category_id=?", (std,))}
lmn_ids = {r[0] for r in c.execute("select test_id from rate_category_tests where rate_category_id=?", (lmn,))}

extra = lmn_ids - std_ids
print(f"\nLMN has {len(lmn_ids)} tests, Standard has {len(std_ids)}")
print(f"LMN extras (not in Standard): {len(extra)}")
for tid in extra:
    row = c.execute("select code, name, is_active, is_panel from tests where id=?", (tid,)).fetchone()
    is_child = c.execute("select 1 from panel_parameters where test_id=? limit 1", (tid,)).fetchone()
    print(f"  id={tid} code={row[0]} name={row[1]!r} active={row[2]} panel={row[3]} child_of_panel={bool(is_child)}")

print(f"\nLMN missing from Standard: {len(std_ids - lmn_ids)}")

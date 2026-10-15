import sqlite3
c = sqlite3.connect("instance/database.db")
ids = [r[0] for r in c.execute("select id from tests where adamlab_id is null")]
print("original test ids:", len(ids))
if ids:
    ph = ",".join("?"*len(ids))
    for tbl, col in [
        ("order_items","test_id"),
        ("panel_parameters","panel_id"),
        ("panel_parameters","test_id"),
        ("test_reference_ranges","test_id"),
    ]:
        try:
            n = c.execute(f"select count(*) from {tbl} where {col} in ({ph})", ids).fetchone()[0]
            print(f"{tbl}.{col} referencing originals:", n)
        except Exception as e:
            print(f"{tbl}.{col} error:", e)

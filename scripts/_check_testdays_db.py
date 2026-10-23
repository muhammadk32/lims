import sqlite3
c = sqlite3.connect("instance/database.db")
print("TestDays 25 and nearby:")
for r in c.execute("select adamlab_id, description, report_date, report_time from test_days where adamlab_id in (25, 23, 24, 26, 27)"):
    print(r)
print()
print("total test_days:", c.execute("select count(*) from test_days").fetchone()[0])
print("sample all test_days ids:", [r[0] for r in c.execute("select adamlab_id from test_days order by adamlab_id")])

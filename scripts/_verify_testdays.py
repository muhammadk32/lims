import sqlite3
c = sqlite3.connect("instance/database.db")
print("=== TestDays table (from AdamLab) ===")
for r in c.execute("select adamlab_id, description, report_date, report_time from test_days order by adamlab_id limit 15"):
    print(r)
print()
print("=== sample tests with their turnaround_hours + adamlab TestDays ===")
# We don't have TestDays stored on Test — verify what we need
for r in c.execute("select code, name, turnaround_hours from tests where adamlab_id is not null order by id limit 5"):
    print(r)

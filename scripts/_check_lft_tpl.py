import sqlite3
c = sqlite3.connect("instance/database.db")
# 1893 = LFTs
for r in c.execute("select id, methodology_html, suggestion_html, interpretation_html, comments_html from pcr_templates where test_id=1893"):
    print("id:", r[0])
    for i, col in enumerate(["methodology","suggestion","interpretation","comments"], 1):
        if r[i]:
            print(f"  {col}: {r[i][:300]}")

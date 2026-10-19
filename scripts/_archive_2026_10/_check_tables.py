import sqlite3
c = sqlite3.connect('instance/database.db')
names = ('test_parameters','specimens','specimen_categories','lab_departments',
         'lab_sections','sub_departments','rate_categories','antimicrobials',
         'antimicrobial_groups','culture_bacteria','culture_medicines',
         'test_default_results','test_remark_templates','test_days','test_cutoffs')
for n in names:
    row = c.execute("select name from sqlite_master where type='table' and name=?", (n,)).fetchone()
    print(n, 'OK' if row else 'MISSING')
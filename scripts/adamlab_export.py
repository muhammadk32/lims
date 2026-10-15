"""
Export AdamLab (SQL Server) catalog tables -> JSON.
Read-only. Writes to scripts/adamlab_import/.
"""
import json
import os
import pyodbc

OUT = os.path.join(os.path.dirname(__file__), "adamlab_import")
os.makedirs(OUT, exist_ok=True)

CONN = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=localhost\\SQLEXPRESS;"
    "DATABASE=adamlab;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

# table -> (pk column, order by)
TABLES = {
    "labtestdetail": ("testcode", "testcode"),
    "TestHead": ("ID", "ID"),
    "TestParameter": ("ID", "ID"),
    "TestParameterNormalValue": ("ID", "ID"),
    "testreferencevalue": (None, None),
    "bkreferencevalue": (None, None),
    "specimen": ("specimencode", "specimencode"),
    "specimencategory": ("scategorycode", "scategorycode"),
    "labdepartment": ("departmentcode", "departmentcode"),
    "labsection": ("sectioncode", "sectioncode"),
    "subdepartment": ("subdepartmentcode", "subdepartmentcode"),
    "subdepartmenttestdetail": (None, None),
    "ratelist": (None, None),
    "ratelist1": (None, None),
    "ratelistcategory": ("rlcatcode", "rlcatcode"),
    "ratelistcategoryrate": (None, None),
    "ratelistcategorytestdetail": (None, None),
    "packagetestdetail": ("packagedetailcode", "packagedetailcode"),
    "testgroupdetail": ("groupdetailcode", "groupdetailcode"),
    "testdefaultresult": (None, None),
    "testremarks": ("recordid", "recordid"),
    "TestDays": ("ID", "ID"),
    "TestCutoffValues": (None, None),
    "TestResultTextType": (None, None),
    "TextTypeResult": (None, None),
    "Antimicrobial": ("AntimicrobialID", "AntimicrobialID"),
    "AntimicrobialGroups": ("Code", "Code"),
    "culturebacteria": ("bacteriacode", "bacteriacode"),
    "culturemedicine": ("medicinecode", "medicinecode"),
    "CultureSensitivity": (None, None),
}

def rows(cur, table, order_col):
    sql = f"SELECT * FROM [{table}]"
    if order_col:
        sql += f" ORDER BY [{order_col}]"
    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    for r in cur.fetchall():
        row = {}
        for c, v in zip(cols, r):
            # normalize datetime/decimal to JSON-safe
            if hasattr(v, "isoformat"):
                v = v.isoformat(sep=" ", timespec="seconds")
            elif isinstance(v, (bytes, bytearray)):
                v = v.decode("utf-8", "replace")
            elif v is not None and type(v).__name__ == "Decimal":
                v = float(v)
            row[c] = v
        yield row

def main():
    cn = pyodbc.connect(CONN, timeout=15)
    cur = cn.cursor()
    for table, (_, order_col) in TABLES.items():
        try:
            data = list(rows(cur, table, order_col))
        except Exception as e:
            print(f"SKIP {table}: {e}")
            continue
        path = os.path.join(OUT, f"{table}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        print(f"{table:35s} {len(data):6d} rows -> {path}")
    cn.close()

if __name__ == "__main__":
    main()
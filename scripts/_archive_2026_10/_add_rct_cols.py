"""Insert discount_percent + commission_percent into RateCategoryTest class."""
import io, os
path = os.path.join("modules", "tests", "models.py")
with io.open(path, "r", encoding="utf-8", newline="") as f:
    src = f.read()
nl = "\r\n" if "\r\n" in src else "\n"

anchor = (
"    test_id = db.Column(db.Integer, db.ForeignKey('tests.id', ondelete='CASCADE'), nullable=False, index=True)" + nl +
"    sort_order = db.Column(db.Integer, default=0)" + nl +
"    rate_category = db.relationship('RateCategory')" + nl +
"    test = db.relationship('Test')"
)

replacement = (
"    test_id = db.Column(db.Integer, db.ForeignKey('tests.id', ondelete='CASCADE'), nullable=False, index=True)" + nl +
"    sort_order = db.Column(db.Integer, default=0)" + nl +
"    discount_percent = db.Column(db.Float, nullable=True)" + nl +
"    commission_percent = db.Column(db.Float, nullable=True)" + nl +
"    rate_category = db.relationship('RateCategory')" + nl +
"    test = db.relationship('Test')"
)

if anchor in src:
    src = src.replace(anchor, replacement, 1)
    print("columns inserted into RateCategoryTest")
else:
    print("ANCHOR MISS")

with io.open(path, "w", encoding="utf-8", newline="") as f:
    f.write(src)
print("done")

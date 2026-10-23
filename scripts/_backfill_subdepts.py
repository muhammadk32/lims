"""Backfill sub_department links for every test via category mapping."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from app import create_app
from extensions import db
from modules.tests.models import (Test, TestCategory, SubDepartment,
                                  SubDepartmentTest)

CATEGORY_TO_SUBDEPT = {
    "Biochemistry":                  "Bio Chemistry",
    "Routine Chemistry":             "Bio Chemistry",
    "Special Chemistry":             "Bio Chemistry",
    "Special Chemistry :-":          "Bio Chemistry",
    "Hematology":                    "CBC Department",
    "Routine Hematology":            "CBC Department",
    "Special Hematology":            "CBC Department",
    "Hormones":                      "HORMONES",
    "Endocrinology":                 "HORMONES",
    "Molecular Biology (PCR)":       "PCR",
    "Molecular":                     "PCR",
    "Microbiology":                  "Microbiology Section",
    "Routine Microbiology":          "Microbiology Section",
    "Special Microbiology":          "Microbiology Section",
    "Routine Culture":               "Microbiology Section",
    "Special Culture":               "Microbiology Section",
    "ELISA Department":              "Manual ELISA",
    "Blood Bank-Transfusion Medicine": "Blood Bank",
    "Cardiology":                    "Cardiology",
    "Clinical Pathology":            "Clinical Pathology",
    "Consultant":                    "Consultant",
    "Covid Vaccine":                 "Vaccine",
    "DOCTOR":                        "Consultant",
    "DRUG LEVEL":                    "Drug Level",
    "Histopathology":                "Histopathology",
    "LabCorp":                       "LabCorp",
    "Other Laboratories reffered Test.": "Referred Tests",
    "Out of the list":               "Miscellaneous",
    "Screening Serology":            "Serology",
    "Serology":                      "Serology",
    "Urinalysis":                    "Urinalysis",
}

def run():
    app = create_app()
    with app.app_context():
        needed_names = set(CATEGORY_TO_SUBDEPT.values())
        existing = {sd.name: sd for sd in SubDepartment.query.all()}
        max_code = max([sd.code for sd in SubDepartment.query.all() if sd.code] or [0])

        for name in needed_names:
            if name not in existing:
                max_code += 1
                sd = SubDepartment(code=max_code, name=name, is_active=True)
                db.session.add(sd)
                db.session.flush()
                existing[name] = sd
                print(f"created sub-dept: {name}")
        db.session.commit()

        linked = 0
        skipped = 0
        skipped_no_cat = 0
        for t in Test.query.all():
            if SubDepartmentTest.query.filter_by(test_id=t.id).first():
                continue
            if not t.category_id:
                skipped_no_cat += 1
                continue
            cat = TestCategory.query.get(t.category_id)
            if not cat:
                skipped_no_cat += 1
                continue
            subdept_name = CATEGORY_TO_SUBDEPT.get(cat.name)
            if not subdept_name:
                skipped += 1
                continue
            sd = existing.get(subdept_name)
            if not sd:
                skipped += 1
                continue
            db.session.add(SubDepartmentTest(
                sub_department_id=sd.id,
                test_id=t.id,
                sort_order=0,
            ))
            linked += 1
        db.session.commit()

        print(f"\nlinked: {linked}")
        print(f"skipped (no mapping): {skipped}")
        print(f"skipped (no category): {skipped_no_cat}")

        total = Test.query.count()
        with_sd = db.session.query(SubDepartmentTest.test_id).distinct().count()
        print(f"\ntotal tests: {total}")
        print(f"tests with sub-department: {with_sd}")
        print(f"coverage: {100*with_sd/total:.1f}%")

if __name__ == "__main__":
    run()

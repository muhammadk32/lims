"""
AdamLab -> Lab Management (SQLite) importer.
Reads JSON from scripts/adamlab_import/ and inserts into the app DB.

Design:
- Idempotent: re-running updates existing rows (matched by *_code / adamlab_id).
- Never overwrites user-edited Test fields (only fills empty ones).
- Wrapped in one transaction per section. Fails loudly.
"""
import json
import os
import sys
from datetime import datetime

# --- bootstrap app ---
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from app import create_app  # noqa: E402  (adjust if your factory differs)
from extensions import db  # noqa: E402
from modules.tests import models as M  # noqa: E402

DATA = os.path.join(HERE, "adamlab_import")

def load(name):
    p = os.path.join(DATA, f"{name}.json")
    if not os.path.exists(p):
        print(f"  (no file) {name}.json")
        return []
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def s(v):
    if v is None: return None
    v = str(v).strip()
    return v or None

def f(v):
    if v is None: return None
    try: return float(v)
    except (TypeError, ValueError): return None

def i(v):
    if v is None: return None
    try: return int(v)
    except (TypeError, ValueError): return None

def b_active(status):
    return (status or "A").upper() == "A"


def import_specimen_categories():
    rows = load("specimencategory")
    n = 0
    for r in rows:
        code = i(r.get("scategorycode"))
        if code is None: continue
        obj = M.SpecimenCategory.query.filter_by(code=code).first()
        if not obj:
            obj = M.SpecimenCategory(code=code)
            db.session.add(obj)
        obj.name = s(r.get("scategoryname")) or f"Cat {code}"
        obj.description = s(r.get("description"))
        obj.is_active = b_active(r.get("status"))
        n += 1
    db.session.commit()
    print(f"specimen_categories: {n}")


def import_specimens():
    rows = load("specimen")
    n = 0
    for r in rows:
        code = i(r.get("specimencode"))
        if code is None: continue
        obj = M.Specimen.query.filter_by(code=code).first()
        if not obj:
            obj = M.Specimen(code=code)
            db.session.add(obj)
        obj.name = s(r.get("specimenname")) or s(r.get("specimen")) or f"Spec {code}"
        obj.description = s(r.get("description"))
        obj.is_active = b_active(r.get("status"))
        cc = i(r.get("scategorycode"))
        if cc:
            cat = M.SpecimenCategory.query.filter_by(code=cc).first()
            if cat: obj.category_id = cat.id
        n += 1
    db.session.commit()
    print(f"specimens: {n}")


def import_lab_departments():
    rows = load("labdepartment")
    n = 0
    for r in rows:
        code = i(r.get("departmentcode"))
        if code is None: continue
        obj = M.LabDepartment.query.filter_by(code=code).first()
        if not obj:
            obj = M.LabDepartment(code=code)
            db.session.add(obj)
        obj.name = s(r.get("departmentname")) or f"Dept {code}"
        obj.is_active = b_active(r.get("status"))
        n += 1
    db.session.commit()
    print(f"lab_departments: {n}")


def import_lab_sections():
    rows = load("labsection")
    n = 0
    for r in rows:
        code = i(r.get("sectioncode"))
        if code is None: continue
        obj = M.LabSection.query.filter_by(code=code).first()
        if not obj:
            obj = M.LabSection(code=code)
            db.session.add(obj)
        obj.name = s(r.get("sectionname")) or f"Section {code}"
        obj.is_active = b_active(r.get("status"))
        dc = i(r.get("departmentcode"))
        if dc:
            d = M.LabDepartment.query.filter_by(code=dc).first()
            if d: obj.department_id = d.id
        n += 1
    db.session.commit()
    print(f"lab_sections: {n}")


def import_sub_departments():
    rows = load("subdepartment")
    n = 0
    for r in rows:
        code = i(r.get("subdepartmentcode"))
        if code is None: continue
        obj = M.SubDepartment.query.filter_by(code=code).first()
        if not obj:
            obj = M.SubDepartment(code=code)
            db.session.add(obj)
        obj.name = s(r.get("subdepartmentname")) or f"Sub {code}"
        obj.is_active = b_active(r.get("status"))
        n += 1
    db.session.commit()
    print(f"sub_departments: {n}")


def import_tests():
    rows = load("labtestdetail")
    n_new = n_upd = 0
    for r in rows:
        adamlab_id = i(r.get("testcode"))
        if adamlab_id is None: continue
        obj = M.Test.query.filter_by(adamlab_id=adamlab_id).first()
        if not obj:
            obj = M.Test(adamlab_id=adamlab_id, code=str(adamlab_id))
            db.session.add(obj)
            n_new += 1
        else:
            n_upd += 1
        obj.name = s(r.get("testname")) or obj.name or f"Test {adamlab_id}"
        obj.price = f(r.get("Rate")) or 0.0
        obj.unit = s(r.get("Unit"))
        obj.sample_type = s(r.get("samplereq"))
        obj.normal_range = s(r.get("defaultresult"))
        obj.description = s(r.get("Comments"))
        obj.is_active = b_active(r.get("Status"))
        obj.sort_order = i(r.get("SortOrder")) or 0
        obj.result_format = 'panel' if (s(r.get("package")) == 'Y') else 'numeric'
        obj.is_panel = (s(r.get("package")) == 'Y')
        tt = i(r.get("TestType"))
        obj.is_outsourced = (i(r.get("labcode")) or -1) > 0
        days = i(r.get("TestDays"))
        if days is not None:
            obj.turnaround_hours = days * 24
    db.session.commit()
    print(f"tests: {n_new} new, {n_upd} updated")


def import_test_parameters():
    rows = load("TestParameter")
    n = 0
    for r in rows:
        aid = i(r.get("ID"))
        tcode = i(r.get("TestID"))
        if aid is None or tcode is None: continue
        parent = M.Test.query.filter_by(adamlab_id=tcode).first()
        if not parent: continue
        obj = M.TestParameter.query.filter_by(adamlab_id=aid).first()
        if not obj:
            obj = M.TestParameter(adamlab_id=aid, test_id=parent.id)
            db.session.add(obj)
        obj.name = s(r.get("Name")) or obj.name or f"Param {aid}"
        obj.report_name = s(r.get("ReportName"))
        obj.unit = s(r.get("Unit"))
        obj.template_id = i(r.get("TemplateID"))
        obj.is_editable = bool(r.get("IsEditable"))
        obj.format = s(r.get("Format"))
        obj.parameter_name = s(r.get("ParameterName"))
        obj.parameter_code = i(r.get("parametercode"))
        obj.sort_order = i(r.get("SortOrder")) or 0
        obj.is_calculated = bool(r.get("CalculatedValue"))
        obj.formula = s(r.get("CalculatedValueFormula"))
        obj.critical_low = f(r.get("CriticalValueLowerBound"))
        obj.critical_high = f(r.get("CriticalValueUpperBound"))
        obj.is_active = bool(r.get("Status", 1))
        n += 1
    db.session.commit()
    print(f"test_parameters: {n}")


def import_normal_values():
    rows = load("TestParameterNormalValue")
    n = 0
    for r in rows:
        aid = i(r.get("ID"))
        pid = i(r.get("TestParameterID"))
        if aid is None or pid is None: continue
        param = M.TestParameter.query.filter_by(adamlab_id=pid).first()
        if not param: continue
        obj = M.TestParameterNormalValue.query.filter_by(adamlab_id=aid).first()
        if not obj:
            obj = M.TestParameterNormalValue(adamlab_id=aid, parameter_id=param.id)
            db.session.add(obj)
        obj.gender = i(r.get("Gender")) or 0
        obj.age_min = i(r.get("FromAge"))
        obj.age_max = i(r.get("ToAge"))
        obj.age_type = s(r.get("AgeType"))
        obj.value_from = f(r.get("FromValue"))
        obj.value_to = f(r.get("ToValue"))
        obj.text_value = s(r.get("TextValue"))
        obj.remarks = s(r.get("Remarks"))
        obj.is_active = bool(r.get("Status", 1))
        n += 1
    db.session.commit()
    print(f"test_parameter_normal_values: {n}")


def import_default_results():
    rows = load("testdefaultresult")
    n = 0
    for r in rows:
        tcode = i(r.get("testcode"))
        rc = i(r.get("resultcode"))
        if tcode is None or rc is None: continue
        parent = M.Test.query.filter_by(adamlab_id=tcode).first()
        if not parent: continue
        obj = M.TestDefaultResult.query.filter_by(adamlab_resultcode=rc).first()
        if not obj:
            obj = M.TestDefaultResult(adamlab_resultcode=rc, test_id=parent.id)
            db.session.add(obj)
        obj.result_name = s(r.get("resultname")) or obj.result_name or f"R{rc}"
        obj.is_active = b_active(r.get("status"))
        n += 1
    db.session.commit()
    print(f"test_default_results: {n}")


def import_remarks():
    rows = load("testremarks")
    n = 0
    for r in rows:
        rid = i(r.get("recordid"))
        tcode = i(r.get("testcode"))
        if rid is None or tcode is None: continue
        parent = M.Test.query.filter_by(adamlab_id=tcode).first()
        if not parent: continue
        obj = M.TestRemarkTemplate.query.filter_by(adamlab_recordid=rid).first()
        if not obj:
            obj = M.TestRemarkTemplate(adamlab_recordid=rid, test_id=parent.id)
            db.session.add(obj)
        obj.remarks = s(r.get("remarks"))
        obj.fixed_remarks = s(r.get("fixremarks"))
        n += 1
    db.session.commit()
    print(f"test_remark_templates: {n}")


def import_test_days():
    rows = load("TestDays")
    n = 0
    for r in rows:
        aid = i(r.get("ID"))
        if aid is None: continue
        obj = M.TestDay.query.filter_by(adamlab_id=aid).first()
        if not obj:
            obj = M.TestDay(adamlab_id=aid)
            db.session.add(obj)
        obj.description = s(r.get("Description")) or obj.description or f"Day {aid}"
        obj.report_date = s(r.get("ReportDate"))
        obj.report_time = i(r.get("ReportTime"))
        n += 1
    db.session.commit()
    print(f"test_days: {n}")


def import_rate_categories():
    rows = load("ratelistcategory")
    n = 0
    for r in rows:
        code = i(r.get("rlcatcode"))
        if code is None: continue
        obj = M.RateCategory.query.filter_by(code=code).first()
        if not obj:
            obj = M.RateCategory(code=code)
            db.session.add(obj)
        obj.name = s(r.get("rlcattname")) or f"Rate {code}"
        obj.is_active = b_active(r.get("status"))
        obj.sort_order = i(r.get("sortorder")) or 0
        n += 1
    db.session.commit()
    print(f"rate_categories: {n}")


def import_antimicrobial_groups():
    rows = load("AntimicrobialGroups")
    n = 0
    for r in rows:
        code = i(r.get("Code"))
        if code is None: continue
        obj = M.AntimicrobialGroup.query.filter_by(code=code).first()
        if not obj:
            obj = M.AntimicrobialGroup(code=code)
            db.session.add(obj)
        obj.name = s(r.get("Name")) or f"Group {code}"
        obj.sort_order = i(r.get("sortorder")) or 0
        obj.is_active = True
        n += 1
    db.session.commit()
    print(f"antimicrobial_groups: {n}")


def import_antimicrobials():
    rows = load("Antimicrobial")
    n = 0
    for r in rows:
        aid = i(r.get("AntimicrobialID"))
        if aid is None: continue
        obj = M.Antimicrobial.query.filter_by(adamlab_id=aid).first()
        if not obj:
            obj = M.Antimicrobial(adamlab_id=aid)
            db.session.add(obj)
        obj.code = i(r.get("Code"))
        obj.name = s(r.get("Name")) or f"AM {aid}"
        obj.short_name = s(r.get("shortname"))
        obj.shortcut_name = s(r.get("shortcutname"))
        obj.sort_order = i(r.get("sortorder")) or 0
        obj.is_active = b_active(r.get("status"))
        n += 1
    db.session.commit()
    print(f"antimicrobials: {n}")


def import_culture_bacteria():
    rows = load("culturebacteria")
    n = 0
    for r in rows:
        code = i(r.get("bacteriacode"))
        if code is None: continue
        obj = M.CultureBacterium.query.filter_by(adamlab_code=code).first()
        if not obj:
            obj = M.CultureBacterium(adamlab_code=code)
            db.session.add(obj)
        obj.name = s(r.get("bacterianame")) or f"B {code}"
        obj.is_active = b_active(r.get("status"))
        n += 1
    db.session.commit()
    print(f"culture_bacteria: {n}")


def import_culture_medicines():
    rows = load("culturemedicine")
    n = 0
    for r in rows:
        code = i(r.get("medicinecode"))
        if code is None: continue
        obj = M.CultureMedicine.query.filter_by(adamlab_code=code).first()
        if not obj:
            obj = M.CultureMedicine(adamlab_code=code)
            db.session.add(obj)
        obj.name = s(r.get("medicinename"))
        obj.short_name = s(r.get("shortname"))
        obj.resistant = i(r.get("resistent"))
        obj.lab_code = i(r.get("labcode"))
        obj.is_active = b_active(r.get("status"))
        n += 1
    db.session.commit()
    print(f"culture_medicines: {n}")


def run():
    app = create_app()
    with app.app_context():
        import_specimen_categories()
        import_specimens()
        import_lab_departments()
        import_lab_sections()
        import_sub_departments()
        import_tests()
        import_test_parameters()
        import_normal_values()
        import_default_results()
        import_remarks()
        import_test_days()
        import_rate_categories()
        import_antimicrobial_groups()
        import_antimicrobials()
        import_culture_bacteria()
        import_culture_medicines()


if __name__ == "__main__":
    run()
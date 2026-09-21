"""
Pre-load common lab tests + categories.
Run via: python -m modules.tests.seed
Or call seed_tests() from app startup (idempotent — safe to run multiple times).
"""
from extensions import db
from .models import Test, TestCategory


# Master list: (code, name, category, price, unit, normal_range)
COMMON_TESTS = [
    # ---------- Hematology ----------
    ('CBC',     'Complete Blood Count',              'Hematology',   15.0, 'cells/µL',  'See report'),
    ('HB',      'Hemoglobin',                        'Hematology',    5.0, 'g/dL',      '13.0 - 17.0'),
    ('WBC',     'White Blood Cell Count',            'Hematology',    6.0, 'x10^9/L',   '4.0 - 11.0'),
    ('PLT',     'Platelet Count',                    'Hematology',    6.0, 'x10^9/L',   '150 - 450'),
    ('ESR',     'Erythrocyte Sedimentation Rate',    'Hematology',    5.0, 'mm/hr',     '0 - 20'),

    # ---------- Biochemistry ----------
    ('FBS',     'Fasting Blood Sugar',               'Biochemistry',  5.0, 'mg/dL',     '70 - 100'),
    ('RBS',     'Random Blood Sugar',                'Biochemistry',  5.0, 'mg/dL',     '70 - 140'),
    ('HBA1C',   'HbA1c (Glycated Hemoglobin)',       'Biochemistry', 18.0, '%',         '< 5.7'),
    ('CHOL',    'Total Cholesterol',                 'Biochemistry',  8.0, 'mg/dL',     '< 200'),
    ('TG',      'Triglycerides',                     'Biochemistry',  8.0, 'mg/dL',     '< 150'),
    ('HDL',     'HDL Cholesterol',                   'Biochemistry',  8.0, 'mg/dL',     '> 40'),
    ('LDL',     'LDL Cholesterol',                   'Biochemistry',  8.0, 'mg/dL',     '< 100'),
    ('CREA',    'Serum Creatinine',                  'Biochemistry',  7.0, 'mg/dL',     '0.7 - 1.3'),
    ('BUN',     'Blood Urea Nitrogen',               'Biochemistry',  7.0, 'mg/dL',     '7 - 20'),
    ('ALT',     'Alanine Aminotransferase (ALT)',    'Biochemistry',  9.0, 'U/L',       '7 - 56'),
    ('AST',     'Aspartate Aminotransferase (AST)',  'Biochemistry',  9.0, 'U/L',       '10 - 40'),
    ('ALP',     'Alkaline Phosphatase',              'Biochemistry',  9.0, 'U/L',       '44 - 147'),
    ('TBIL',    'Total Bilirubin',                   'Biochemistry',  8.0, 'mg/dL',     '0.1 - 1.2'),
    ('ALB',     'Serum Albumin',                     'Biochemistry',  8.0, 'g/dL',      '3.5 - 5.0'),

    # ---------- Endocrinology ----------
    ('TSH',     'Thyroid Stimulating Hormone',       'Endocrinology', 20.0, 'mIU/L',    '0.4 - 4.0'),
    ('T3',      'Triiodothyronine (T3)',             'Endocrinology', 18.0, 'ng/dL',    '80 - 200'),
    ('T4',      'Thyroxine (T4)',                    'Endocrinology', 18.0, 'µg/dL',    '5.0 - 12.0'),

    # ---------- Serology / Immunology ----------
    ('CRP',     'C-Reactive Protein',                'Serology',      12.0, 'mg/L',     '< 5'),
    ('RF',      'Rheumatoid Factor',                 'Serology',      15.0, 'IU/mL',    '< 14'),
    ('HBSAG',   'Hepatitis B Surface Antigen',       'Serology',      18.0, 'Index',    'Negative'),
    ('HCV',     'Hepatitis C Antibody',              'Serology',      20.0, 'Index',    'Negative'),
    ('HIV',     'HIV 1 & 2 Antibodies',              'Serology',      25.0, 'Index',    'Negative'),
    ('WIDAL',   'Widal Test',                        'Serology',      15.0, 'Titer',    'See report'),
    ('DENGUE',  'Dengue NS1 Antigen',                'Serology',      28.0, 'Index',    'Negative'),
    ('MAL',     'Malaria Antigen',                   'Serology',      15.0, 'Index',    'Negative'),

    # ---------- Urine / Stool ----------
    ('URINE',   'Complete Urine Analysis',           'Urinalysis',     8.0, '—',        'See report'),
    ('UCS',     'Urine Culture & Sensitivity',       'Microbiology',  25.0, 'CFU/mL',   'No growth'),
    ('STOOL',   'Stool Routine Examination',         'Microbiology',   8.0, '—',        'See report'),
]


def seed_tests():
    """Idempotent — only inserts missing tests/categories."""
    created_tests = 0
    created_categories = 0

    for code, name, cat_name, price, unit, normal_range in COMMON_TESTS:
        # Category
        cat = TestCategory.query.filter_by(name=cat_name).first()
        if not cat:
            cat = TestCategory(name=cat_name)
            db.session.add(cat)
            db.session.flush()
            created_categories += 1

        # Test
        if not Test.query.filter_by(code=code).first():
            db.session.add(Test(
                code=code,
                name=name,
                category_id=cat.id,
                price=price,
                unit=unit,
                normal_range=normal_range,
            ))
            created_tests += 1

    db.session.commit()
    return created_tests, created_categories
"""
Lab Test models.
- TestCategory: groups tests (Hematology, Biochemistry, etc.)
- Test:         a single lab test OR a panel (container of parameters)
- PanelParameter: junction linking a panel to its parameter tests (many-to-many)
"""
from extensions import db
from core.models import BaseModel


# ============================================================
# Result format choices (used in forms + UI)
# ============================================================
RESULT_FORMATS = [
    ('numeric',     'Numeric (e.g. 5.4 mg/dL)'),
    ('qualitative', 'Qualitative (Positive / Negative)'),
    ('semi_quant',  'Semi-quantitative (Trace, 1+, 2+)'),
    ('titre',       'Titre (1:40, 1:80, ...)'),
    ('pcr',         'PCR / Molecular'),
    ('histopath',   'Histopathology / Narrative'),
    ('culture',     'Culture & Sensitivity'),
    ('microscopy',  'Microscopy / Text Fields'),
    ('panel',       'Panel (contains multiple tests)'),
]

RESULT_FORMAT_KEYS = [k for k, _ in RESULT_FORMATS]
RESULT_FORMAT_MAP = dict(RESULT_FORMATS)


# ============================================================
# TEST CATEGORY
# ============================================================
class TestCategory(BaseModel):
    """Groups tests: Hematology, Biochemistry, Microbiology, etc."""
    __tablename__ = 'test_categories'

    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    tests = db.relationship('Test', backref='category_ref', lazy=True)

    def __repr__(self):
        return f'<TestCategory {self.name}>'


# ============================================================
# TEST (single test OR panel)
# ============================================================
class Test(BaseModel):
    """
    A lab test offered by the lab.

    Can be:
      - A standalone test (is_panel=False) — has its own unit + range
      - A panel (is_panel=True) — contains child tests via PanelParameter
    """
    __tablename__ = 'tests'

    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    adamlab_id = db.Column(db.Integer, unique=True, nullable=True, index=True)
    category_id = db.Column(
        db.Integer,
        db.ForeignKey('test_categories.id'),
        nullable=True
    )

    price = db.Column(db.Float, default=0.0, nullable=False)
    normal_range = db.Column(db.String(120), nullable=True)
    unit = db.Column(db.String(30), nullable=True)
    description = db.Column(db.Text, nullable=True)

    turnaround_hours = db.Column(db.Integer, default=24)
    sample_type = db.Column(db.String(120), nullable=True)  # e.g. EDTA whole blood
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # ---------- Outsourced / referral test ----------
    # When True, this test is performed by a partner lab. The discount
    # applied to it is capped at max_discount_percent.
    is_outsourced = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        index=True,
    )

    # Maximum discount % allowed for this test. NULL = no cap.
    max_discount_percent = db.Column(db.Float, nullable=True)

    # Which partner lab performs this test (only meaningful when is_outsourced=True)
    laboratory_id = db.Column(
        db.Integer,
        db.ForeignKey('laboratories.id'),
        nullable=True,
        index=True,
    )
    laboratory_ref = db.relationship('Laboratory', foreign_keys=[laboratory_id])

    # ---------- Panel / format fields (Phase 1) ----------
    # Section marker inside a panel (Physical / Chemical / Microscopy?)
    panel_section = db.Column(db.String(40), nullable=True)

    result_format = db.Column(
        db.String(20),
        default='numeric',
        nullable=False,
        index=True,
    )
    is_panel = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        index=True,
    )
    sort_order = db.Column(
        db.Integer,
        default=0,
        nullable=False,
    )

    # ---------- Helper properties ----------
    @property
    def is_standalone(self):
        """True if this is a regular test (not a panel)."""
        return not self.is_panel

    @property
    def parameter_count(self):
        """Number of child parameters (0 for standalone tests)."""
        if not self.is_panel:
            return 0
        return PanelParameter.query.filter_by(panel_id=self.id).count()

    def get_parameters(self):
        """
        Return the panel's parameter tests in display order.
        Returns an empty list for standalone tests.
        """
        if not self.is_panel:
            return []
        return (
            Test.query
            .join(PanelParameter, PanelParameter.test_id == Test.id)
            .filter(PanelParameter.panel_id == self.id)
            .order_by(PanelParameter.sort_order, Test.name)
            .all()
        )

    @property
    def format_label(self):
        """Human-readable label for the result format."""
        return RESULT_FORMAT_MAP.get(self.result_format, self.result_format)

    def __repr__(self):
        kind = 'PANEL' if self.is_panel else 'TEST'
        return f'<Test {self.code} ({kind}) — {self.name}>'


# ============================================================
# PANEL PARAMETER (junction: panel â†” child test)
# ============================================================
class PanelParameter(db.Model):
    """
    Links a panel to its child tests. Many-to-many:
    - One panel can have many tests
    - One test can belong to many panels (e.g., Hemoglobin in CBC, Anemia Panel, ...)
    """
    __tablename__ = 'panel_parameters'

    id = db.Column(db.Integer, primary_key=True)
    panel_id = db.Column(
        db.Integer,
        db.ForeignKey('tests.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    test_id = db.Column(
        db.Integer,
        db.ForeignKey('tests.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    sort_order = db.Column(db.Integer, default=0, nullable=False)

    # Relationships
    panel = db.relationship(
        'Test',
        foreign_keys=[panel_id],
        backref=db.backref(
            'panel_parameters',
            cascade='all, delete-orphan',
            order_by='PanelParameter.sort_order',
        ),
    )
    test = db.relationship(
        'Test',
        foreign_keys=[test_id],
        backref=db.backref('parameter_of_panels', lazy='dynamic'),
    )

    # Prevent the same test being added twice to the same panel
    __table_args__ = (
        db.UniqueConstraint('panel_id', 'test_id', name='uq_panel_test'),
    )

    def __repr__(self):
        return f'<PanelParameter panel={self.panel_id} test={self.test_id} order={self.sort_order}>'

# ============================================================
# TestReferenceRange — multi-range normal values per test
# ============================================================
class TestReferenceRange(BaseModel):
    """A single reference range for a test, keyed by gender + age bracket.

    Ranges are matched at report time using the patient's gender and age.
    If a test has no ranges, the older Test.normal_range column is used.
    """
    __tablename__ = 'test_reference_ranges'

    test_id = db.Column(
        db.Integer,
        db.ForeignKey('tests.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )

    # 'male' | 'female' | 'any'
    gender = db.Column(db.String(10), nullable=False, default='any')

    # Age bracket in years (nullable = no bound)
    age_min_years = db.Column(db.Integer, nullable=True)
    age_max_years = db.Column(db.Integer, nullable=True)

    # Sub-year bracket in days (for neonates). Takes priority over years when age < 1.
    age_min_days = db.Column(db.Integer, nullable=True)
    age_max_days = db.Column(db.Integer, nullable=True)

    # Unit-aware bounds (as entered by user)
    age_min_value = db.Column(db.Integer, nullable=True)
    age_min_unit  = db.Column(db.String(10), nullable=True)   # days|weeks|months|years
    age_max_value = db.Column(db.Integer, nullable=True)
    age_max_unit  = db.Column(db.String(10), nullable=True)

    # The range string (e.g. "13.5 - 17.5")
    range_text = db.Column(db.String(120), nullable=False)

    # Optional per-range unit override
    unit = db.Column(db.String(30), nullable=True)

    # Optional critical value threshold (free text, e.g. "< 7.0 or > 20.0")
    critical_value = db.Column(db.String(120), nullable=True)

    # Free-text notes (rendered as HTML from the rich editor)
    notes = db.Column(db.Text, nullable=True)

    sort_order = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    # Relationship back to Test
    test = db.relationship(
        'Test',
        backref=db.backref(
            'reference_ranges',
            cascade='all, delete-orphan',
            order_by='TestReferenceRange.sort_order',
        ),
    )

    def __repr__(self):
        return f'<RefRange test={self.test_id} {self.gender} {self.range_text}>'



# ============================================================
# PcrTemplate — per-test reusable Methodology / Suggestion /
# Interpretation / Comments blocks for PCR-format tests.
# ============================================================
class PcrTemplate(BaseModel):
    """Per-test default text blocks shown on PCR entry + reports.

    One row per Test. The entry page pre-fills its tab editors from
    these values, but a specific order can override them (the override
    lives on Result.method_html etc.). Reports prefer the per-order
    Result.* value, falling back to this template.
    """
    __tablename__ = 'pcr_templates'

    test_id = db.Column(
        db.Integer,
        db.ForeignKey('tests.id', ondelete='CASCADE'),
        nullable=False,
        unique=True,
        index=True,
    )

    methodology_html    = db.Column(db.Text, nullable=True)
    suggestion_html     = db.Column(db.Text, nullable=True)
    interpretation_html = db.Column(db.Text, nullable=True)
    comments_html       = db.Column(db.Text, nullable=True)

    test = db.relationship('Test', backref=db.backref(
        'pcr_template', uselist=False, cascade='all, delete-orphan'
    ))

    def __repr__(self):
        return f'<PcrTemplate test={self.test_id}>'


# ============================================================
# LABORATORY (partner / referral lab)
# ============================================================


# ============================================================
# IMPORTED FROM ADAMLAB (SQL Server) — hybrid schema additions
# ============================================================

class SpecimenCategory(BaseModel):
    __tablename__ = 'specimen_categories'
    code = db.Column(db.Integer, unique=True, nullable=True, index=True)  # adamlab scategorycode
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)


class Specimen(BaseModel):
    __tablename__ = 'specimens'
    code = db.Column(db.Integer, unique=True, nullable=True, index=True)  # adamlab specimencode
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('specimen_categories.id'), nullable=True)
    category = db.relationship('SpecimenCategory')
    is_active = db.Column(db.Boolean, nullable=False, default=True)


class LabDepartment(BaseModel):
    __tablename__ = 'lab_departments'
    code = db.Column(db.Integer, unique=True, nullable=True, index=True)
    name = db.Column(db.String(120), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)


class LabSection(BaseModel):
    __tablename__ = 'lab_sections'
    code = db.Column(db.Integer, unique=True, nullable=True, index=True)
    name = db.Column(db.String(120), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('lab_departments.id'), nullable=True)
    department = db.relationship('LabDepartment')
    is_active = db.Column(db.Boolean, nullable=False, default=True)


class SubDepartment(BaseModel):
    __tablename__ = 'sub_departments'
    code = db.Column(db.Integer, unique=True, nullable=True, index=True)
    name = db.Column(db.String(120), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)


class SubDepartmentTest(BaseModel):
    __tablename__ = 'sub_department_tests'
    sub_department_id = db.Column(db.Integer, db.ForeignKey('sub_departments.id', ondelete='CASCADE'), nullable=False, index=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id', ondelete='CASCADE'), nullable=False, index=True)
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    sub_department = db.relationship('SubDepartment')
    test = db.relationship('Test')


class TestParameter(BaseModel):
    """AdamLab TestParameter — per-test analyte row (child of Test).

    This is different from PanelParameter: a panel links to standalone Tests.
    TestParameter represents an *analyte inside a single test* (e.g. WBC,
    Neutrophils inside a CBC). Carries its own unit, format, and formula.
    """
    __tablename__ = 'test_parameters'
    adamlab_id = db.Column(db.Integer, unique=True, nullable=True, index=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id', ondelete='CASCADE'), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    report_name = db.Column(db.String(120), nullable=True)
    unit = db.Column(db.String(60), nullable=True)
    template_id = db.Column(db.Integer, nullable=True)
    is_editable = db.Column(db.Boolean, nullable=False, default=True)
    format = db.Column(db.String(20), nullable=True)
    parameter_name = db.Column(db.String(60), nullable=True)
    parameter_code = db.Column(db.Integer, nullable=True)
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    is_calculated = db.Column(db.Boolean, nullable=False, default=False)
    formula = db.Column(db.String(500), nullable=True)
    critical_low = db.Column(db.Float, nullable=True)
    critical_high = db.Column(db.Float, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    test = db.relationship('Test', backref=db.backref('parameters', cascade='all, delete-orphan'))


class TestParameterNormalValue(BaseModel):
    __tablename__ = 'test_parameter_normal_values'
    adamlab_id = db.Column(db.Integer, unique=True, nullable=True, index=True)
    parameter_id = db.Column(db.Integer, db.ForeignKey('test_parameters.id', ondelete='CASCADE'), nullable=False, index=True)
    gender = db.Column(db.Integer, nullable=False, default=1)   # 0=any, 1=male, 2=female (adamlab convention)
    age_min = db.Column(db.Integer, nullable=True)
    age_max = db.Column(db.Integer, nullable=True)
    age_type = db.Column(db.String(20), nullable=True)          # years|months|days
    value_from = db.Column(db.Float, nullable=True)
    value_to = db.Column(db.Float, nullable=True)
    text_value = db.Column(db.Text, nullable=True)
    remarks = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    parameter = db.relationship('TestParameter', backref=db.backref('normal_values', cascade='all, delete-orphan'))


class TestDefaultResult(BaseModel):
    __tablename__ = 'test_default_results'
    adamlab_resultcode = db.Column(db.Integer, unique=True, nullable=True, index=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id', ondelete='CASCADE'), nullable=False, index=True)
    result_name = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    test = db.relationship('Test', backref=db.backref('default_results', cascade='all, delete-orphan'))


class TestRemarkTemplate(BaseModel):
    __tablename__ = 'test_remark_templates'
    adamlab_recordid = db.Column(db.Integer, unique=True, nullable=True, index=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id', ondelete='CASCADE'), nullable=False, index=True)
    remarks = db.Column(db.Text, nullable=True)
    fixed_remarks = db.Column(db.Text, nullable=True)
    test = db.relationship('Test', backref=db.backref('remark_templates', cascade='all, delete-orphan'))


class TestDay(BaseModel):
    __tablename__ = 'test_days'
    adamlab_id = db.Column(db.Integer, unique=True, nullable=True, index=True)
    description = db.Column(db.String(120), nullable=False)
    report_date = db.Column(db.String(60), nullable=True)
    report_time = db.Column(db.Integer, nullable=True)


class TestCutoff(BaseModel):
    __tablename__ = 'test_cutoffs'
    test_code = db.Column(db.String(60), nullable=True, index=True)
    parameter = db.Column(db.String(120), nullable=False)
    cutoff_value = db.Column(db.String(80), nullable=True)


class RateCategory(BaseModel):
    __tablename__ = 'rate_categories'
    code = db.Column(db.Integer, unique=True, nullable=True, index=True)
    name = db.Column(db.String(120), nullable=False)
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)


class RateCategoryRate(BaseModel):
    __tablename__ = 'rate_category_rates'
    rate_category_id = db.Column(db.Integer, db.ForeignKey('rate_categories.id', ondelete='CASCADE'), nullable=False, index=True)
    company_code = db.Column(db.Integer, nullable=True, index=True)
    section_code = db.Column(db.Integer, nullable=True, index=True)
    rate_percent = db.Column(db.Numeric(18, 0), nullable=True)
    commission = db.Column(db.Numeric(8, 0), nullable=True)
    rate_category = db.relationship('RateCategory', backref=db.backref('rates', cascade='all, delete-orphan'))


class RateCategoryTest(BaseModel):
    __tablename__ = 'rate_category_tests'
    rate_category_id = db.Column(db.Integer, db.ForeignKey('rate_categories.id', ondelete='CASCADE'), nullable=False, index=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id', ondelete='CASCADE'), nullable=False, index=True)
    sort_order = db.Column(db.Integer, default=0)
    rate_category = db.relationship('RateCategory')
    test = db.relationship('Test')


class AntimicrobialGroup(BaseModel):
    __tablename__ = 'antimicrobial_groups'
    code = db.Column(db.Integer, unique=True, nullable=True, index=True)
    name = db.Column(db.String(150), nullable=False)
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)


class Antimicrobial(BaseModel):
    __tablename__ = 'antimicrobials'
    adamlab_id = db.Column(db.Integer, unique=True, nullable=True, index=True)
    code = db.Column(db.Integer, nullable=True, index=True)
    name = db.Column(db.String(150), nullable=False)
    short_name = db.Column(db.String(10), nullable=True)
    shortcut_name = db.Column(db.String(15), nullable=True)
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)


class CultureBacterium(BaseModel):
    __tablename__ = 'culture_bacteria'
    adamlab_code = db.Column(db.Integer, unique=True, nullable=True, index=True)
    name = db.Column(db.String(500), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)


class CultureMedicine(BaseModel):
    __tablename__ = 'culture_medicines'
    adamlab_code = db.Column(db.Integer, unique=True, nullable=True, index=True)
    name = db.Column(db.String(120), nullable=True)
    short_name = db.Column(db.String(40), nullable=True)
    resistant = db.Column(db.Integer, nullable=True)
    lab_code = db.Column(db.Integer, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

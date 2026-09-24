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
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # ---------- Panel / format fields (Phase 1) ----------
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
# PANEL PARAMETER (junction: panel ↔ child test)
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

    # The range string (e.g. "13.5 - 17.5")
    range_text = db.Column(db.String(120), nullable=False)

    # Optional per-range unit override
    unit = db.Column(db.String(30), nullable=True)

    # Optional critical value threshold (free text, e.g. "< 7.0 or > 20.0")
    critical_value = db.Column(db.String(120), nullable=True)

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

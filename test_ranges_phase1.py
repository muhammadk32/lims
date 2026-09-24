"""
Phase 1 — Test reference ranges (gender + age + critical).

Adds:
  - TestReferenceRange model
  - DB table (created via __table__.create)
  - modules/tests/ranges.py — matching + evaluation logic
  - Read-only section on /tests/<id> view page

Nothing else changes. Existing normal_range column stays as fallback.
"""
import os

# ============================================================
# 1. Model — TestReferenceRange
# ============================================================
mp = 'modules/tests/models.py'
m = open(mp, encoding='utf-8').read()

if 'class TestReferenceRange' not in m:
    new_model = '''

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
'''
    m = m + new_model
    with open(mp, 'w', encoding='utf-8') as f:
        f.write(m)
    print('OK  - TestReferenceRange model added to modules/tests/models.py')
else:
    print('SKIP - model already exists')


# ============================================================
# 2. Create DB table
# ============================================================
print()
print('Creating DB table...')
from app import app
from extensions import db
from modules.tests.models import TestReferenceRange

with app.app_context():
    try:
        TestReferenceRange.__table__.create(db.engine, checkfirst=True)
        print('  + test_reference_ranges table ready')
    except Exception as e:
        print(f'  ! {e}')


# ============================================================
# 3. Service — modules/tests/ranges.py
# ============================================================
sp = 'modules/tests/ranges.py'
service = '''"""
Reference-range matching + critical-value evaluation.

Matching priority (first match wins):
  1. Exact gender + exact age bracket
  2. Exact gender (age = any)
  3. 'any' gender + exact age bracket
  4. 'any' gender (age = any)
  5. Fallback → test.normal_range (no critical check)

A range is only evaluated if `is_active` is True.
"""
from .models import TestReferenceRange


def _all_ranges(test):
    """Active ranges for a test, ordered."""
    if not test:
        return []
    return [r for r in (test.reference_ranges or []) if r.is_active]


def _age_matches(rng, age):
    """True if age (int years) falls in [min, max] (inclusive)."""
    if age is None:
        # If patient age unknown, only match ranges with no age bounds
        return rng.age_min_years is None and rng.age_max_years is None

    if rng.age_min_years is not None and age < rng.age_min_years:
        return False
    if rng.age_max_years is not None and age > rng.age_max_years:
        return False
    return True


def pick_range(test, gender=None, age=None):
    """Return the best-matching TestReferenceRange, or None."""
    if not test:
        return None

    g = (gender or '').strip().lower()
    if g not in ('male', 'female'):
        g = None

    ranges = _all_ranges(test)
    if not ranges:
        return None

    # Priority order
    for want_gender, want_exact_age in (
        (g, True),        # 1. exact gender + exact age
        (g, False),       # 2. exact gender (any age)
        ('any', True),    # 3. any gender + exact age
        ('any', False),   # 4. any gender (any age)
    ):
        if want_gender is None:
            continue
        for r in ranges:
            if (r.gender or 'any').lower() != want_gender:
                continue
            if want_exact_age:
                if _age_matches(r, age):
                    return r
            else:
                if r.age_min_years is None and r.age_max_years is None:
                    return r

    return None


def resolve_range_text(test, gender=None, age=None):
    """Return the range string to display. Falls back to test.normal_range."""
    r = pick_range(test, gender, age)
    if r and r.range_text:
        return r.range_text
    return (test.normal_range if test else None) or ''


def resolve_unit(test, gender=None, age=None):
    """Return unit for the matched range, or test.unit."""
    r = pick_range(test, gender, age)
    if r and r.unit:
        return r.unit
    return (test.unit if test else None) or ''


def resolve_critical(test, gender=None, age=None):
    """Return the critical value threshold string (or None)."""
    r = pick_range(test, gender, age)
    if r and r.critical_value:
        return r.critical_value
    return None


def evaluate(test, value, gender=None, age=None):
    """Return (flag, is_critical).

    flag: 'normal' | 'abnormal' | 'critical' | 'unknown'
    """
    if value is None or value == '':
        return 'unknown', False

    try:
        from modules.results.validators import check_result
    except Exception:
        return 'unknown', False

    range_text = resolve_range_text(test, gender, age)
    if not range_text:
        return 'unknown', False

    try:
        flag = check_result(range_text, value)
    except Exception:
        flag = 'unknown'

    critical = False
    crit_text = resolve_critical(test, gender, age)
    if crit_text:
        try:
            crit_flag = check_result(crit_text, value)
            critical = (crit_flag == 'abnormal')
        except Exception:
            critical = False

    if critical:
        return 'critical', True
    return flag, False


# ============================================================
# Demo / manual seeding helper
# ============================================================
def add_range(test, gender, range_text, age_min=None, age_max=None,
              unit=None, critical_value=None, sort_order=0):
    """Convenience helper to attach a range. Caller commits."""
    from extensions import db

    r = TestReferenceRange(
        test_id=test.id,
        gender=(gender or 'any').lower(),
        age_min_years=age_min,
        age_max_years=age_max,
        range_text=range_text,
        unit=unit,
        critical_value=critical_value,
        sort_order=sort_order,
        is_active=True,
    )
    db.session.add(r)
    return r
'''

with open(sp, 'w', encoding='utf-8') as f:
    f.write(service)
print('OK  - modules/tests/ranges.py created')


# ============================================================
# 4. Read-only view section on /tests/<id>
# ============================================================
# First, inject the ranges into the view context
rp = 'modules/tests/routes.py'
r = open(rp, encoding='utf-8').read()

old_view = '''@tests_bp.route('/<int:test_id>')
@login_required
def view_test(test_id):
    test = _get_test_or_404(test_id)
    return render_template('tests/view.html', test=test)'''

new_view = '''@tests_bp.route('/<int:test_id>')
@login_required
def view_test(test_id):
    test = _get_test_or_404(test_id)
    return render_template(
        'tests/view.html',
        test=test,
        ranges=[r for r in (test.reference_ranges or []) if r.is_active],
    )'''

if old_view in r:
    r = r.replace(old_view, new_view, 1)
    with open(rp, 'w', encoding='utf-8') as f:
        f.write(r)
    print('OK  - tests/routes.py: view_test passes ranges to template')
else:
    print('WARN - view_test anchor not found')


# ============================================================
# 5. Add the range table to the view template
# ============================================================
tp = 'modules/tests/templates/tests/view.html'
t = open(tp, encoding='utf-8').read()

if 'Reference Ranges' not in t and 'reference-ranges' not in t:
    # Insert a "Reference Ranges" card after the main card
    marker = "{% endblock %}"
    section = '''

  {# ============ REFERENCE RANGES (Phase 1 read-only) ============ #}
  {% if ranges %}
  <div class="card border-0 shadow-sm mt-3">
    <div class="card-header bg-white border-bottom d-flex justify-content-between align-items-center">
      <h6 class="fw-bold mb-0">
        <i class="bi bi-sliders2"></i> Reference Ranges
        <span class="badge bg-secondary ms-2">{{ ranges|length }}</span>
      </h6>
      <span class="text-muted small">Matched by patient gender &amp; age at report time</span>
    </div>
    <div class="table-responsive">
      <table class="table table-sm align-middle mb-0">
        <thead class="table-light">
          <tr>
            <th style="width: 110px;">Gender</th>
            <th style="width: 140px;">Age Bracket</th>
            <th>Range</th>
            <th style="width: 90px;">Unit</th>
            <th>Critical Value</th>
          </tr>
        </thead>
        <tbody>
          {% for r in ranges %}
          <tr>
            <td><span class="badge bg-info text-dark">{{ r.gender|capitalize }}</span></td>
            <td class="text-muted small">
              {% if r.age_min_years is not none and r.age_max_years is not none %}
                {{ r.age_min_years }} – {{ r.age_max_years }} yrs
              {% elif r.age_min_years is not none %}
                ≥ {{ r.age_min_years }} yrs
              {% elif r.age_max_years is not none %}
                ≤ {{ r.age_max_years }} yrs
              {% else %}
                Any age
              {% endif %}
            </td>
            <td class="fw-semibold">{{ r.range_text }}</td>
            <td class="text-muted">{{ r.unit or test.unit or '—' }}</td>
            <td>
              {% if r.critical_value %}
                <span class="text-danger fw-semibold">{{ r.critical_value }}</span>
              {% else %}
                <span class="text-muted">—</span>
              {% endif %}
            </td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
    <div class="card-footer bg-white border-top">
      <span class="text-muted small">
        <i class="bi bi-info-circle"></i>
        If a test has no ranges matching the patient's gender/age, the universal range applies:
        <strong>{{ test.normal_range or '—' }}</strong>
      </span>
    </div>
  </div>
  {% endif %}

'''
    idx = t.rfind(marker)
    if idx != -1:
        t = t[:idx] + section + t[idx:]
        with open(tp, 'w', encoding='utf-8') as f:
            f.write(t)
        print('OK  - tests/view.html: read-only ranges section added')
    else:
        print('WARN - endblock not found in view template')
else:
    print('SKIP - ranges section already present')


print()
print('=' * 60)
print('Phase 1 done.')
print()
print('Next: add a few ranges manually with a small script, then')
print('      check /tests/<id> to see them.')
print('=' * 60)

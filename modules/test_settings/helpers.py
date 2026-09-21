"""
Small helpers for the Lab Test Settings module.

Kept intentionally lightweight — used by routes and (later) by templates
via context processors.
"""
from extensions import db
from modules.tests import Test, TestCategory, RESULT_FORMATS, RESULT_FORMAT_KEYS


# ============================================================
# Format statistics
# ============================================================
def format_counts():
    """
    Return {format_key: count} for all active tests.
    Every key in RESULT_FORMAT_KEYS is guaranteed to be present (0 if unused).
    """
    counts = {key: 0 for key in RESULT_FORMAT_KEYS}

    rows = (
        db.session.query(Test.result_format, db.func.count(Test.id))
        .filter(Test.is_active == True)          # noqa: E712
        .group_by(Test.result_format)
        .all()
    )
    for key, n in rows:
        if key in counts:
            counts[key] = n
        else:
            counts.setdefault(key, n)

    return counts


def category_counts():
    """
    Return {category_id: count} for all active tests.
    Uses None key for uncategorized tests.
    """
    counts = {None: 0}

    rows = (
        db.session.query(Test.category_id, db.func.count(Test.id))
        .filter(Test.is_active == True)          # noqa: E712
        .group_by(Test.category_id)
        .all()
    )
    for cat_id, n in rows:
        counts[cat_id] = n
    return counts


def catalog_stats():
    """
    Return a dict of top-level numbers used by the settings UI header.
    """
    total_tests = Test.query.filter(Test.is_active == True).count()   # noqa: E712
    total_panels = Test.query.filter(
        Test.is_active == True,                    # noqa: E712
        Test.is_panel == True,                     # noqa: E712
    ).count()
    total_categories = TestCategory.query.count()
    uncategorized = Test.query.filter(
        Test.is_active == True,                    # noqa: E712
        Test.category_id.is_(None),
    ).count()

    return {
        'total_tests': total_tests,
        'total_panels': total_panels,
        'total_standalone': total_tests - total_panels,
        'total_categories': total_categories,
        'uncategorized': uncategorized,
    }


# ============================================================
# Safe coercion helpers
# ============================================================
def safe_int(value, default=None):
    """Convert to int, return default on failure."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value, default=None):
    """Convert to float, return default on failure."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


# ============================================================
# Format label lookup
# ============================================================
FORMAT_LABELS = dict(RESULT_FORMATS)


def format_label(key: str) -> str:
    """Human-readable label for a result format key."""
    return FORMAT_LABELS.get(key, key or '—')


# ============================================================
# Format visual hints (used by templates — icon + color)
# ============================================================
FORMAT_META = {
    'numeric':     {'icon': 'bi-123',              'color': '#0d6efd'},
    'qualitative': {'icon': 'bi-patch-question',   'color': '#6f42c1'},
    'semi_quant':  {'icon': 'bi-bar-chart-steps',  'color': '#fd7e14'},
    'titre':       {'icon': 'bi-123',              'color': '#20c997'},
    'pcr':         {'icon': 'bi-virus',            'color': '#dc3545'},
    'histopath':   {'icon': 'bi-journal-medical',  'color': '#6c757d'},
    'culture':     {'icon': 'bi-droplet-half',     'color': '#198754'},
    'microscopy':  {'icon': 'bi-eyedropper',       'color': '#0dcaf0'},
    'panel':       {'icon': 'bi-collection',       'color': '#6610f2'},
}


def format_meta(key: str) -> dict:
    """Return icon + color hints for a format key."""
    return FORMAT_META.get(key, {'icon': 'bi-circle', 'color': '#6c757d'})
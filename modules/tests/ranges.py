"""
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


def _has_age_bounds(r):
    return r.age_min_years is not None or r.age_max_years is not None


def pick_range(test, gender=None, age=None):
    """Return the best-matching TestReferenceRange, or None.

    Match tiers (first hit wins):
      1. Exact gender + range has age bounds + age fits
      2. Exact gender + range has NO age bounds
      3. 'any' gender + range has age bounds + age fits
      4. 'any' gender + range has NO age bounds

    If age is None (unknown), only tier 2 and 4 apply.
    """
    if not test:
        return None

    g = (gender or '').strip().lower()
    if g not in ('male', 'female'):
        g = None

    ranges = _all_ranges(test)
    if not ranges:
        return None

    # Helper: find a range matching the given gender that has age bounds
    # and whose bounds include the patient's age.
    def find_age_specific(want_gender):
        if age is None:
            return None
        for r in ranges:
            if (r.gender or 'any').lower() != want_gender:
                continue
            if not _has_age_bounds(r):
                continue
            if _age_matches(r, age):
                return r
        return None

    # Helper: find a range matching the given gender with NO age bounds.
    def find_age_any(want_gender):
        for r in ranges:
            if (r.gender or 'any').lower() != want_gender:
                continue
            if not _has_age_bounds(r):
                return r
        return None

    # Tier 1: exact gender + age-specific
    if g:
        r = find_age_specific(g)
        if r:
            return r

    # Tier 2: exact gender + age-agnostic
    if g:
        r = find_age_any(g)
        if r:
            return r

    # Tier 3: any gender + age-specific
    r = find_age_specific('any')
    if r:
        return r

    # Tier 4: any gender + age-agnostic
    r = find_age_any('any')
    if r:
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

"""
modules/tests/ranges.py
Reference-range resolution + evaluation.
Aligned with Patient model:
    gender          -> 'Male' / 'Female' / 'Other'
    age             -> int (preferred)
    date_of_birth   -> Date (fallback)
"""
from __future__ import annotations
import re
from datetime import date


# ---------------- CONFIG ----------------
PATIENT_GENDER_FIELD = 'gender'
PATIENT_AGE_FIELD    = 'age'              # integer age, preferred
PATIENT_DOB_FIELD    = 'date_of_birth'    # fallback if age is None
# ----------------------------------------


def _norm_gender(g):
    if not g:
        return 'any'
    g = str(g).strip().lower()
    if g in ('m', 'male'):
        return 'male'
    if g in ('f', 'female'):
        return 'female'
    return 'any'


def patient_age_years(patient):
    """Return patient age in whole years, or None."""
    if patient is None:
        return None

    # Prefer stored integer age
    if PATIENT_AGE_FIELD:
        v = getattr(patient, PATIENT_AGE_FIELD, None)
        try:
            if v is not None and str(v).strip() != '':
                return int(v)
        except (TypeError, ValueError):
            pass

    # Fallback: compute from DOB
    if PATIENT_DOB_FIELD:
        dob = getattr(patient, PATIENT_DOB_FIELD, None)
        if not dob:
            return None
        if isinstance(dob, str):
            try:
                dob = date.fromisoformat(dob[:10])
            except ValueError:
                return None
        today = date.today()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    return None


def patient_gender(patient):
    if patient is None:
        return 'any'
    return _norm_gender(getattr(patient, PATIENT_GENDER_FIELD, None))


def _age_ok(rng, age):
    if rng.age_min_years is None and rng.age_max_years is None:
        return True
    if age is None:
        return False
    if rng.age_min_years is not None and age < rng.age_min_years:
        return False
    if rng.age_max_years is not None and age > rng.age_max_years:
        return False
    return True


def pick_range(test, gender, age):
    """
    Priority (bounded beats unbounded, at every gender tier):
      1. exact gender + bounded age
      2. 'any'    gender + bounded age
      3. exact gender + unbounded
      4. 'any'    gender + unbounded
    """
    if test is None:
        return None
    g = _norm_gender(gender)
    rows = [r for r in getattr(test, 'reference_ranges', []) if r.is_active]
    if not rows:
        return None
    rows.sort(key=lambda r: (r.sort_order or 0, r.id or 0))

    def bounded(r):
        return r.age_min_years is not None or r.age_max_years is not None

    gender_order = [g] if g == 'any' else [g, 'any']

    # Pass 1: bounded-age ranges (exact gender first, then 'any')
    for want_gender in gender_order:
        for r in rows:
            if _norm_gender(r.gender) == want_gender and bounded(r) and _age_ok(r, age):
                return r

    # Pass 2: unbounded ranges (exact gender first, then 'any')
    for want_gender in gender_order:
        for r in rows:
            if _norm_gender(r.gender) == want_gender and not bounded(r):
                return r

    return None

def resolve_range_text(test, gender, age):
    r = pick_range(test, gender, age)
    if r and r.range_text:
        return r.range_text
    return getattr(test, 'normal_range', '') or ''


def resolve_critical(test, gender, age):
    r = pick_range(test, gender, age)
    return r.critical_value if (r and r.critical_value) else None


# -------- numeric evaluation --------

_NUM = r'-?\d+(?:\.\d+)?'
_RANGE_RE = re.compile(rf'({_NUM})\s*(?:-|–|to)\s*({_NUM})', re.IGNORECASE)
_CRIT_RE  = re.compile(rf'([<>]=?)\s*({_NUM})')


def _to_float(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def evaluate(test, value, gender, age):
    """
    Returns (flag, is_critical)
      flag        : 'normal' | 'abnormal' | 'unknown'
      is_critical : True if a critical threshold was crossed
    """
    v = _to_float(value)
    if v is None:
        return ('unknown', False)

    crit_txt = resolve_critical(test, gender, age)
    is_crit = False
    if crit_txt:
        for op, num in _CRIT_RE.findall(crit_txt):
            n = _to_float(num)
            if n is None:
                continue
            if op == '<'  and v <  n: is_crit = True
            if op == '<=' and v <= n: is_crit = True
            if op == '>'  and v >  n: is_crit = True
            if op == '>=' and v >= n: is_crit = True

    rng_txt = resolve_range_text(test, gender, age)
    if not rng_txt:
        return ('unknown', is_crit)

    m = _RANGE_RE.search(rng_txt)
    if not m:
        return ('unknown', is_crit)
    lo, hi = _to_float(m.group(1)), _to_float(m.group(2))
    if lo is None or hi is None:
        return ('unknown', is_crit)

    if lo <= v <= hi:
        return ('normal', is_crit)
    return ('abnormal', is_crit)


def evaluate_patient(test, value, patient):
    """Convenience: pass a Patient object directly."""
    return evaluate(test, value, patient_gender(patient), patient_age_years(patient))


# ===== Phase 3: consumer helpers =====
def resolve_range_for_order(test, order):
    """
    One-call helper for templates and PDF builders.
    Returns the range string for the order's patient.
    Falls back to test.normal_range if no matching reference range.
    """
    if test is None:
        return ''
    if order is None:
        return getattr(test, 'normal_range', '') or ''
    patient = getattr(order, 'patient', None)
    g = patient_gender(patient)
    a = patient_age_years(patient)
    return resolve_range_text(test, g, a)


def evaluate_for_order(test, value, order):
    """
    Same as evaluate(), but takes an order instead of (gender, age).
    Returns (flag, is_critical).
    """
    if test is None or order is None:
        return ('unknown', False)
    patient = getattr(order, 'patient', None)
    return evaluate(test, value, patient_gender(patient), patient_age_years(patient))

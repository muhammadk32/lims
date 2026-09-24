"""Business logic for tests + reference ranges.

No HTTP, no flash, no redirect. Pure domain operations.
"""
from extensions import db
from core.audit import log_action
from .models import TestReferenceRange


def _int_or_none(s):
    s = (s or '').strip()
    return int(s) if s.lstrip('-').isdigit() else None


def _str_or_none(s):
    s = (s or '').strip()
    return s or None


def save_ranges(test, form, user):
    """Upsert all ranges for one test from parallel-array form lists.

    Form fields:
        gender[], age_min[], age_max[], range_text[],
        unit[], critical_value[], sort_order[]

    Blank range_text → skipped.
    Ranges on the test but missing from POST → is_active=False.

    Returns (created, updated, deleted).
    """
    if test is None:
        return 0, 0, 0

    genders  = form.getlist('gender[]')
    age_mins = form.getlist('age_min[]')
    age_maxs = form.getlist('age_max[]')
    age_min_ds = form.getlist('age_min_days[]')
    age_max_ds = form.getlist('age_max_days[]')
    texts    = form.getlist('range_text[]')
    units    = form.getlist('unit[]')
    crits    = form.getlist('critical_value[]')
    orders   = form.getlist('sort_order[]')

    existing = {r.id: r for r in (test.reference_ranges or [])}
    seen_ids = set()
    created = updated = 0

    for i, raw_text in enumerate(texts):
        text = (raw_text or '').strip()
        if not text:
            continue

        row = TestReferenceRange(test_id=test.id)
        db.session.add(row)
        created += 1

        row.gender         = (genders[i] if i < len(genders) else 'any') or 'any'
        row.age_min_years  = _int_or_none(age_mins[i] if i < len(age_mins) else '')
        row.age_max_years  = _int_or_none(age_maxs[i] if i < len(age_maxs) else '')
        row.age_min_days   = _int_or_none(age_min_ds[i] if i < len(age_min_ds) else '')
        row.age_max_days   = _int_or_none(age_max_ds[i] if i < len(age_max_ds) else '')
        row.range_text     = text
        row.unit           = _str_or_none(units[i] if i < len(units) else '')
        row.critical_value = _str_or_none(crits[i] if i < len(crits) else '')
        row.sort_order     = _int_or_none(orders[i] if i < len(orders) else '') or 0
        row.is_active      = True

    # Soft-delete ranges that were on the test but not in this POST
    deleted = 0
    for rid, row in existing.items():
        if rid not in seen_ids and row.is_active:
            row.is_active = False
            deleted += 1

    db.session.commit()

    log_action(
        'update', 'test', test.id,
        f'Ranges saved: +{created} -{deleted}'
    )
    return created, updated, deleted

# ============================================================
# Per-gender reference value row (ADAM-style Add flow)
# ============================================================
def _int_or_none_loose(s):
    s = (s or "").strip()
    if not s:
        return None
    try:
        return int(float(s))
    except (TypeError, ValueError):
        return None


def _float_or_none(s):
    try:
        return float(str(s).strip())
    except (TypeError, ValueError):
        return None


def _build_range_text(vmin, vmax):
    lo = _float_or_none(vmin)
    hi = _float_or_none(vmax)
    if lo is None and hi is None:
        return ""
    if lo is None:
        return f"< {hi}"
    if hi is None:
        return f"> {lo}"
    return f"{lo} - {hi}"


def _build_critical(cmin, cmax):
    parts = []
    if _float_or_none(cmin):
        parts.append(f"< {_float_or_none(cmin)}")
    if _float_or_none(cmax):
        parts.append(f"> {_float_or_none(cmax)}")
    return " or ".join(parts) or None


def add_range_row(test, gender, form, user):
    """Insert one reference-range row from the ADAM-style form."""
    gender = (gender or "any").lower()

    def _v(k):   return _int_or_none_loose(form.get(k))
    def _u(k):   return (form.get(k) or "years").strip().lower()

    row = TestReferenceRange(
        test_id=test.id,
        gender=gender,
        age_min_value=_v("age_min_value"),
        age_min_unit=_u("age_min_unit"),
        age_max_value=_v("age_max_value"),
        age_max_unit=_u("age_max_unit"),
        range_text=_build_range_text(form.get("value_min"), form.get("value_max")),
        critical_value=_build_critical(form.get("crit_min"), form.get("crit_max")),
        notes=(form.get("notes") or "").strip() or None,
        unit=(form.get("unit") or "").strip() or None,
        sort_order=0,
        is_active=True,
    )
    db.session.add(row)
    db.session.commit()
    log_action("create", "test_reference_range", row.id,
               f"Added {gender} range for test {test.id}: {row.range_text}")
    return row


def update_range_row(range_id, form, user):
    row = TestReferenceRange.query.get(range_id)
    if not row:
        return None

    def _v(k):   return _int_or_none_loose(form.get(k))
    def _u(k):   return (form.get(k) or "years").strip().lower()

    row.age_min_value = _v("age_min_value")
    row.age_min_unit  = _u("age_min_unit")
    row.age_max_value = _v("age_max_value")
    row.age_max_unit  = _u("age_max_unit")
    row.range_text     = _build_range_text(form.get("value_min"), form.get("value_max"))
    row.critical_value = _build_critical(form.get("crit_min"), form.get("crit_max"))
    row.notes          = (form.get("notes") or "").strip() or None
    db.session.commit()
    log_action("update", "test_reference_range", row.id, f"Updated range {row.range_text}")
    return row


def delete_range_row(range_id, user):
    row = TestReferenceRange.query.get(range_id)
    if not row:
        return False
    row.is_active = False
    db.session.commit()
    log_action("delete", "test_reference_range", row.id,
               f"Removed range {row.range_text}")
    return True

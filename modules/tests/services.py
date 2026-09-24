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

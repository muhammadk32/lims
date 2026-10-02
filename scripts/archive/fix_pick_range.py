# Rewrite pick_range with strict specificity rules
p = 'modules/tests/ranges.py'
s = open(p, encoding='utf-8').read()

old = '''def pick_range(test, gender=None, age=None):
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

    return None'''

new = '''def _has_age_bounds(r):
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

    return None'''

if old in s:
    s = s.replace(old, new, 1)
    open(p, 'w', encoding='utf-8').write(s)
    print('OK  - pick_range rewritten with strict specificity')
else:
    print('WARN - pick_range not matched, checking...')
    idx = s.find('def pick_range')
    print(s[idx:idx+1200] if idx != -1 else 'not found')

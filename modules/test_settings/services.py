"""Business logic for test settings — mutations only.

No HTTP, no flash, no redirect. Pure domain operations.
"""
from sqlalchemy import func

from extensions import db
from modules.tests import Test, TestCategory, PanelParameter


# ============================================================
# Formats
# ============================================================
def update_test_format(test, new_format):
    """Change a test's result format. Returns dict for JSON response.

    Returns None if the format is invalid (caller raises 400).
    """
    from modules.tests import RESULT_FORMAT_KEYS, RESULT_FORMATS

    if new_format not in RESULT_FORMAT_KEYS:
        return None

    was_panel = test.is_panel
    test.result_format = new_format

    if new_format == 'panel':
        test.is_panel = True
        test.unit = None
        test.normal_range = None
    else:
        test.is_panel = False

    db.session.commit()

    return {
        'ok': True,
        'test_id': test.id,
        'result_format': test.result_format,
        'is_panel': test.is_panel,
        'panel_changed': (was_panel != test.is_panel),
        'label': dict(RESULT_FORMATS).get(test.result_format, test.result_format),
    }


# ============================================================
# Categories
# ============================================================
def create_category(name, description):
    """Create a category. Returns (ok, error, category)."""
    name = (name or '').strip()
    description = (description or '').strip()

    if not name:
        return False, 'Name is required', None
    if len(name) > 80:
        return False, 'Name too long (max 80 chars)', None

    existing = TestCategory.query.filter(
        func.lower(TestCategory.name) == name.lower()
    ).first()
    if existing:
        return False, f'Category "{name}" already exists', None

    cat = TestCategory(name=name, description=description or None)
    db.session.add(cat)
    db.session.commit()
    return True, None, cat


def update_category(cat, name, description):
    """Update a category. Returns (ok, error)."""
    name = (name or '').strip()
    description = (description or '').strip()

    if not name:
        return False, 'Name is required'

    dup = TestCategory.query.filter(
        func.lower(TestCategory.name) == name.lower(),
        TestCategory.id != cat.id,
    ).first()
    if dup:
        return False, f'Category "{name}" already exists'

    cat.name = name
    cat.description = description or None
    db.session.commit()
    return True, None


def delete_category(cat):
    """Delete a category. Returns (ok, error, test_count)."""
    test_count = Test.query.filter(Test.category_id == cat.id).count()
    if test_count > 0:
        return False, f'Cannot delete — {test_count} test(s) still use this category.', test_count

    db.session.delete(cat)
    db.session.commit()
    return True, None, 0


# ============================================================
# Panels
# ============================================================
def _validate_panel_form(code, name, price, panel_id=None):
    """Return (ok, errors_list, price_val)."""
    errors = []

    if not code:
        errors.append('Code is required.')
    if not name:
        errors.append('Name is required.')

    if code:
        dup_query = Test.query.filter(Test.code == code)
        if panel_id is not None:
            dup_query = dup_query.filter(Test.id != panel_id)
        if dup_query.first():
            if panel_id is None:
                errors.append(f'Code "{code}" already exists.')
            else:
                errors.append(f'Code "{code}" already used by another test.')

    price_val = 0.0
    try:
        price_val = float(price or 0)
        if price_val < 0:
            errors.append('Price must be >= 0.')
    except (ValueError, TypeError):
        errors.append('Price must be a number.')

    return (not errors), errors, price_val


def create_panel(form):
    """Create a panel from form data. Returns (ok, errors, panel)."""
    code = (form.get('code') or '').strip().upper()
    name = (form.get('name') or '').strip()
    cat_id = form.get('category_id') or None
    price = form.get('price') or '0'
    description = (form.get('description') or '').strip()
    param_ids = form.getlist('parameter_ids')

    ok, errors, price_val = _validate_panel_form(code, name, price)
    if not ok:
        return False, errors, None

    panel = Test(
        code=code,
        name=name,
        category_id=int(cat_id) if cat_id else None,
        price=price_val,
        description=description or None,
        is_panel=True,
        is_active=True,
        result_format='panel',
        unit=None,
        normal_range=None,
    )
    db.session.add(panel)
    db.session.flush()

    _replace_panel_parameters(panel.id, param_ids)
    db.session.commit()
    return True, [], panel


def update_panel(panel, form):
    """Update an existing panel. Returns (ok, errors)."""
    code = (form.get('code') or '').strip().upper()
    name = (form.get('name') or '').strip()
    cat_id = form.get('category_id') or None
    price = form.get('price') or '0'
    description = (form.get('description') or '').strip()
    param_ids = form.getlist('parameter_ids')

    ok, errors, price_val = _validate_panel_form(code, name, price, panel_id=panel.id)
    if not ok:
        return False, errors

    panel.code = code
    panel.name = name
    panel.category_id = int(cat_id) if cat_id else None
    panel.price = price_val
    panel.description = description or None
    panel.is_active = bool(form.get('is_active', True))

    PanelParameter.query.filter_by(panel_id=panel.id).delete()
    _replace_panel_parameters(panel.id, param_ids)
    db.session.commit()
    return True, []


def delete_panel(panel):
    """Delete a panel and its parameter links. Returns (ok, error)."""
    from modules.orders.models import OrderItem

    used = OrderItem.query.filter_by(test_id=panel.id).count()
    if used > 0:
        return False, f'Cannot delete — {used} order(s) use this panel.'

    PanelParameter.query.filter_by(panel_id=panel.id).delete()
    db.session.delete(panel)
    db.session.commit()
    return True, None


def _replace_panel_parameters(panel_id, param_ids):
    """Insert PanelParameter rows in given order."""
    for i, tid in enumerate(param_ids):
        try:
            tid_int = int(tid)
        except (ValueError, TypeError):
            continue
        db.session.add(PanelParameter(
            panel_id=panel_id,
            test_id=tid_int,
            sort_order=i,
        ))

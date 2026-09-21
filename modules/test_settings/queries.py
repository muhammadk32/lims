"""Query helpers for test settings — pure data-fetching.

No HTTP, no flash, no commits.
"""
from sqlalchemy import func

from extensions import db
from modules.tests import Test, TestCategory, PanelParameter
from .helpers import catalog_stats, format_counts, format_meta


# ============================================================
# Tab 1 — Formats
# ============================================================
def list_formats(q='', fmt_filter='', cat_filter=''):
    """Return the filtered list of active tests."""
    query = Test.query.filter(Test.is_active == True)  # noqa: E712

    if q:
        like = f'%{q}%'
        query = query.filter(
            (Test.code.ilike(like)) | (Test.name.ilike(like))
        )

    if fmt_filter:
        query = query.filter(Test.result_format == fmt_filter)

    if cat_filter:
        try:
            query = query.filter(Test.category_id == int(cat_filter))
        except (ValueError, TypeError):
            pass

    return query.order_by(Test.is_panel.desc(), Test.name.asc()).all()


def list_categories():
    """All categories, alphabetical."""
    return TestCategory.query.order_by(TestCategory.name.asc()).all()


# ============================================================
# Tab 2 — Categories
# ============================================================
def list_categories_with_counts():
    """Return (categories, test_counts_dict, uncategorized_count)."""
    cats = TestCategory.query.order_by(TestCategory.name.asc()).all()

    counts = dict(
        db.session.query(Test.category_id, func.count(Test.id))
        .filter(Test.is_active == True)  # noqa: E712
        .group_by(Test.category_id)
        .all()
    )

    uncategorized = (
        Test.query
        .filter(Test.is_active == True, Test.category_id.is_(None))  # noqa: E712
        .count()
    )

    return cats, counts, uncategorized


# ============================================================
# Tab 4 — Panels
# ============================================================
def list_panels(q=''):
    """Active panels, optionally filtered by search."""
    query = Test.query.filter(
        Test.is_active == True,   # noqa: E712
        Test.is_panel == True,    # noqa: E712
    )
    if q:
        like = f'%{q}%'
        query = query.filter(
            (Test.code.ilike(like)) | (Test.name.ilike(like))
        )
    return query.order_by(Test.name.asc()).all()


def param_counts_by_panel():
    """Return {panel_id: count} for all panels."""
    return dict(
        db.session.query(PanelParameter.panel_id, func.count(PanelParameter.id))
        .group_by(PanelParameter.panel_id)
        .all()
    )


def list_standalone_tests():
    """Active non-panel tests, alphabetical — for panel composition."""
    return (
        Test.query
        .filter(Test.is_active == True, Test.is_panel == False)  # noqa: E712
        .order_by(Test.name.asc())
        .all()
    )


def get_panel_parameters(panel_id):
    """Return ordered PanelParameter rows for a panel."""
    return (
        PanelParameter.query
        .filter_by(panel_id=panel_id)
        .order_by(PanelParameter.sort_order, PanelParameter.id)
        .all()
    )


def count_panel_order_items(panel_id):
    """How many order items reference this panel? (for delete-guard)"""
    from modules.orders.models import OrderItem
    return OrderItem.query.filter_by(test_id=panel_id).count()

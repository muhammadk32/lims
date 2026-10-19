"""Rate-category resolution: compute per-item rate% and commission%."""
def resolve_rate_for_order(order):
    """Return (rate_percent, commission_percent) for this order.

    Looks up the rate category from the company (Laboratory) attached
    to the order. Uses the first RateCategoryRate row for that category
    (ordered by section_code, then id). Returns (0.0, 0.0) when no
    mapping is found.
    """
    if not order.company_id:
        return 0.0, 0.0
    from modules.laboratories.models import Laboratory
    from modules.tests.models import RateCategory, RateCategoryRate
    lab = Laboratory.query.get(order.company_id)
    if not lab or not getattr(lab, "rate_category_id", None):
        return 0.0, 0.0
    rate = (RateCategoryRate.query
            .filter_by(rate_category_id=lab.rate_category_id)
            .order_by(RateCategoryRate.section_code.asc().nulls_last(),
                      RateCategoryRate.id.asc())
            .first())
    if not rate:
        return 0.0, 0.0
    return float(rate.rate_percent or 0.0), float(rate.commission or 0.0)

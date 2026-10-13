"""Per-item discount resolution.

An order has one global discount entered by staff (percent or amount).
But some tests (e.g. outsourced / partner-lab tests) have a hard cap on
how much discount they can carry - see Test.max_discount_percent.

This module computes, per OrderItem, what discount actually applies.

Rules:
  - If the test has max_discount_percent set:
      applied_pct = min(global_pct, test.max_discount_percent)
      source      = 'capped'
  - Else:
      applied_pct = global_pct
      source      = 'global'
  - If global discount is a fixed amount (not percent), we prorate it
    across all billable items proportionally to their price.

NOTE: 'discount_source' is INTERNAL ONLY. It must never be printed on
patient-facing output (bill, receipt, PDF invoice).
"""
from decimal import Decimal, ROUND_HALF_UP


def _money(v):
    return float(Decimal(str(v)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def apply_discounts(order):
    """Populate each top-level OrderItem with its applied discount.

    Call this after all items exist and after order.discount_* is set,
    but before order.recompute_total().

    Returns the total discount amount (float).
    """
    items = [i for i in order.items if i.parent_item_id is None]
    if not items:
        for i in order.items:
            i.applied_discount_pct = 0.0
            i.applied_discount_amount = 0.0
            i.discount_source = 'none'
        return 0.0

    total_subtotal = sum((i.price or 0.0) for i in items) or 0.0

    # ---- Percent-mode global discount ----
    if order.discount_type == 'percent':
        global_pct = max(0.0, min(100.0, order.discount_percent or 0.0))
        total_discount = 0.0
        for i in items:
            cap = None
            if i.test and getattr(i.test, 'max_discount_percent', None) is not None:
                cap = float(i.test.max_discount_percent)

            if cap is not None:
                applied_pct = min(global_pct, cap)
                source = 'capped' if applied_pct < global_pct else 'global'
            else:
                applied_pct = global_pct
                source = 'global'

            amt = _money((i.price or 0.0) * applied_pct / 100.0)
            i.applied_discount_pct = applied_pct
            i.applied_discount_amount = amt
            i.discount_source = source
            total_discount += amt
        return _money(total_discount)

    # ---- Fixed-amount global discount ----
    # Distribute proportionally across items, respecting caps.
    fixed_amt = max(0.0, order.discount_amount or 0.0)
    if fixed_amt <= 0 or total_subtotal <= 0:
        for i in items:
            i.applied_discount_pct = 0.0
            i.applied_discount_amount = 0.0
            i.discount_source = 'none'
        return 0.0

    # Pass 1 - proportional target per item
    target = {}
    for i in items:
        share = (i.price or 0.0) / total_subtotal
        target[i.id] = fixed_amt * share

    # Pass 2 - cap by test policy
    total_discount = 0.0
    for i in items:
        tgt = target[i.id]
        max_amt = None
        if i.test and getattr(i.test, 'max_discount_percent', None) is not None:
            max_amt = (i.price or 0.0) * float(i.test.max_discount_percent) / 100.0

        if max_amt is not None and tgt > max_amt:
            amt = _money(max_amt)
            source = 'capped'
        else:
            amt = _money(tgt)
            source = 'global'

        pct = (amt / (i.price or 1.0)) * 100.0 if i.price else 0.0
        i.applied_discount_pct = _money(pct)
        i.applied_discount_amount = amt
        i.discount_source = source
        total_discount += amt

    return _money(total_discount)
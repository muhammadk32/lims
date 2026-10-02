import re
"""Business logic for results entry.

No HTTP, no flash, no redirect. Pure domain operations.
"""
from datetime import datetime

from extensions import db
from core.audit import log_action
from modules.orders.models import Order, OrderItem, OrderStatus


# ============================================================
# Save results for an order
# ============================================================
def save_order_results(order, form, user):
    """Apply submitted form values to order items.

    Behavior:
      - Saves every result_value_{item_id} and result_notes_{item_id}.
      - Clears per-item correction flags for anything now having a value.
      - If the order was APPROVED and any value changed → reset to COMPLETED
        and clear per-item verification. Returns ('reset', None).
      - If the order was CORRECTION and nothing still needs correction →
        clears order-level correction fields and moves to COMPLETED.
      - Auto-completes when all results are in.

    Returns a tuple (mode, payload):
      ('reset',    order)  — approval was reset (route should redirect to view)
      ('saved',    order)  — normal save
      ('nochange', order)  — nothing changed, still committed
    """
    was_approved = (order.status == OrderStatus.APPROVED)
    was_correction = (order.status == OrderStatus.CORRECTION)
    old_values = {i.id: i.result_value for i in order.items}

    # --- 1. Apply submitted values ---
    for item in order.items:
        key_v = f'result_value_{item.id}'
        key_n = f'result_notes_{item.id}'
        # SKIP items not present in the form ? prevents wiping previously-saved values
        if key_v not in form:
            continue
        value = form.get(key_v, '').strip()
        notes = form.get(key_n, '').strip()
        item.result_value = value or None
        item.result_notes = notes or None

    # --- 1b. Apply PCR extended fields (if any were in the form) ---
    _save_pcr_fields(form, order)
    _save_culture_fields(form, order)

    # --- 2. Detect changes ---
    something_changed = any(
        old_values.get(item.id) != item.result_value
        for item in order.items
    )

    # --- 3. Clear correction flags on items that now have a value ---
    for item in order.items:
        if item.correction_note and item.result_value:
            item.correction_note = None
            item.correction_at = None
            item.correction_by_id = None

    # --- 4. If approved and edited → reset approval, return 'reset' ---
    if was_approved and something_changed:
        order.status = OrderStatus.COMPLETED
        order.reported_at = None
        order.reported_by_id = None

        for top in order.top_level_items:
            if top.is_verified:
                top.verified_at = None
                top.verified_by_id = None

        db.session.commit()
        log_action(
            'result', 'order', order.id,
            f'Edited results of approved order {order.order_code} '
            f'— approval reset, re-approval required',
            extra={'status': order.status},
        )
        return 'reset', order

    # --- 5. If was in CORRECTION and nothing still needs it → clear state ---
    if was_correction:
        still = any(
            getattr(t, 'needs_correction', False)
            for t in order.top_level_items
        ) or any(
            getattr(c, 'needs_correction', False)
            for t in order.top_level_items
            for c in t.children
        )
        if not still:
            order.correction_note = None
            order.correction_at = None
            order.correction_by_id = None
            if order.status == OrderStatus.CORRECTION:
                order.status = OrderStatus.COMPLETED

    # --- 6. Auto-complete when all results are in ---
    if order.all_results_done and order.status != OrderStatus.COMPLETED:
        order.status = OrderStatus.COMPLETED

    db.session.commit()
    log_action(
        'result', 'order', order.id,
        f'Entered results for order {order.order_code}',
        extra={'status': order.status},
    )
    return 'saved', order


# ============================================================
# Clear one result
# ============================================================
def clear_result_value(item, user):
    """Clear a single OrderItem's result and notes.

    Also clears parent verification (if any) and resets an approved
    order to COMPLETED.

    Returns (order, was_approved).
    Raises ValueError with a user-facing message if item isn't editable.
    """
    order = item.order
    if not order:
        raise ValueError('Item does not belong to any order.')
    if order.status == OrderStatus.CANCELLED:
        raise ValueError('Cannot edit a cancelled order.')

    item.result_value = None
    item.result_notes = None

    # Clear per-item verification on the top-level item this belongs to
    top = item if item.parent_item_id is None else item.parent
    if top and top.is_verified:
        top.verified_at = None
        top.verified_by_id = None

    was_approved = (order.status == OrderStatus.APPROVED)
    if was_approved:
        order.status = OrderStatus.COMPLETED
        order.reported_at = None
        order.reported_by_id = None

    db.session.commit()

    log_action(
        'result', 'order_item', item.id,
        f'Cleared result for item {item.id} on order {order.order_code}',
        extra={'order_id': order.id},
    )
    return order, was_approved


# ============================================================
# Patient history
# ============================================================
def get_patient_orders(patient_id):
    """Return non-cancelled orders for a patient, newest first."""
    return (
        Order.query
        .filter(Order.patient_id == patient_id)
        .filter(Order.status != OrderStatus.CANCELLED)
        .order_by(Order.id.desc())
        .all()
    )

# ============================================================
# PCR-STYLE result save
# ============================================================
def save_pcr_result(item, form, user):
    """Upsert the extended PCR fields on Result for one OrderItem."""
    from .models import Result
    from datetime import datetime

    from .models import Result
    r = Result.query.filter_by(order_item_id=item.id).first()
    if r is None:
        r = Result(order_item_id=item.id)
        db.session.add(r)

    def _g(k):
        v = (form.get(k) or "").strip()
        return v or None

    r.specimen            = _g("specimen")
    r.result_type         = _g("result_type")
    r.viral_load_type     = _g("viral_load_type")
    r.no_of_repeat        = form.get("no_of_repeat", type=int)
    r.method_html         = _g("method_html")
    r.suggestion_html     = _g("suggestion_html")
    r.interpretation_html = _g("interpretation_html")
    r.comments_html       = _g("comments_html")
    r.value               = _g("value") or (item.result_value or None)
    r.notes               = _g("notes")
    r.entered_at          = datetime.utcnow()
    if user is not None:
        r.entered_by_id = getattr(user, "id", None)

    # Mirror the short value up to OrderItem so the rest of the app sees it
    item.result_value = r.value
    item.result_notes = r.notes

    db.session.commit()
    return r

def _save_pcr_fields(form, order):
    """Collect any pcr_* fields for items in this order and save them."""
    from .models import Result
    from datetime import datetime

    for item in order.top_level_items:
        prefix = f"pcr_result_type_{item.id}"
        if prefix not in form:
            continue
        r = Result.query.filter_by(order_item_id=item.id).first()
        if r is None:
            r = Result(order_item_id=item.id)
            db.session.add(r)

        r.result_type         = (form.get(f"pcr_result_type_{item.id}") or "").strip() or None
        _pcr_val              = (form.get(f"pcr_result_value_{item.id}") or "").strip() or None
        if _pcr_val:
            r.value = _pcr_val
            item.result_value = _pcr_val
        r.specimen            = (form.get(f"pcr_specimen_{item.id}") or "").strip() or None
        r.viral_load_type     = (form.get(f"pcr_viral_load_{item.id}") or "").strip() or None
        r.no_of_repeat        = form.get(f"pcr_no_of_repeat_{item.id}", type=int)
        r.method_html         = (form.get(f"pcr_method_html_{item.id}") or "").strip() or None
        r.suggestion_html     = (form.get(f"pcr_suggestion_html_{item.id}") or "").strip() or None
        r.interpretation_html = (form.get(f"pcr_interpretation_html_{item.id}") or "").strip() or None
        r.comments_html       = (form.get(f"pcr_comments_html_{item.id}") or "").strip() or None
        r.entered_at = datetime.utcnow()

def _save_culture_fields(form, order):
    """Save microscopy rows + culture organism + antibiotic results."""
    for item in order.top_level_items:
        fmt = (item.test.result_format or '').lower()

        if fmt in ('culture', 'culture_sensitivity'):
            org_key = f"culture_organism_{item.id}"
            if org_key in form:
                # stash organism in item.result_notes (append-only)
                org = form.get(org_key, '').strip()
                abx_rows = []
                for k in form:
                    if k.startswith(f"culture_abx_{item.id}_"):
                        v = form.get(k, '').strip()
                        if v:
                            abx_rows.append(f"{k.rsplit('_',1)[-1]}:{v}")
                combined = f"Organism: {org}" if org else ''
                if abx_rows:
                    combined += "\n" + " | ".join(abx_rows)
                item.result_notes = combined or item.result_notes

# ============================================================
# PER-TEST save (used by /results/item/<id>)
# ============================================================
def save_item_result(item, form, user):
    """Save value + notes for one OrderItem. If it's a panel,
    iterate children and save each child's input too.

    Culture-format tests also persist extended fields + antibiotic grid.
    """
    from datetime import datetime

    now = datetime.utcnow()

    # ---- Culture: extended fields + antibiotic grid ----
    fmt = (item.test.result_format or '').lower()
    if fmt in ('culture', 'culture_sensitivity'):
        save_culture_fields(item, form, user)
        # Mark item as ready for verification (has results)
        if not item.result_value:
            item.result_value = 'Culture'
        db.session.commit()
        return item

    if item.has_children:
        for child in item.children:
            key = f'result_value_{child.id}'
            if key not in form:
                continue
            child.result_value = (form.get(key) or '').strip() or None
            child.result_notes = (form.get(f'result_notes_{child.id}') or '').strip() or None
            if child.result_value:
                child.correction_note = None
                child.correction_at = None
                child.correction_by_id = None
    else:
        key = f'result_value_{item.id}'
        if key in form:
            item.result_value = (form.get(key) or '').strip() or None
            item.result_notes = (form.get(f'result_notes_{item.id}') or '').strip() or None
            if item.result_value:
                item.correction_note = None
                item.correction_at = None
                item.correction_by_id = None

    order = item.order
    if order.status == OrderStatus.APPROVED:
        order.status = OrderStatus.COMPLETED
        order.reported_at = None
        order.reported_by_id = None
        for top in order.top_level_items:
            if top.is_verified:
                top.verified_at = None
                top.verified_by_id = None

    # If everything is filled, mark completed
    if order.all_results_done and order.status not in (OrderStatus.APPROVED, OrderStatus.CORRECTION):
        order.status = OrderStatus.COMPLETED

    db.session.commit()
    log_action('result', 'order_item', item.id,
               f'Entered result for {item.test.code} ({item.test.name})')
    return item

# ============================================================
# Culture fields save (used by /results/item/<id>)
# ============================================================
def save_culture_fields(item, form, user):
    """Save all culture_* fields on the item's Result plus
    the CultureAntibiotic grid rows."""
    from .models import Result
    from core.models import CultureAntibiotic
    from datetime import datetime

    r = Result.query.filter_by(order_item_id=item.id).first()
    if r is None:
        r = Result(order_item_id=item.id)
        db.session.add(r)

    def _g(k):
        v = form.get(k)
        if v is None:
            return None
        v = str(v).strip()
        # treat literal "None" / "null" as empty
        if v.lower() in ('', 'none', 'null'):
            return None
        return v

    # Single-value fields
    r.culture_specimen      = _g(f'culture_specimen_{item.id}')
    r.culture_no_sensitive  = _g(f'culture_no_sensitive_{item.id}')
    r.culture_phage_name    = _g(f'culture_phage_name_{item.id}')
    r.culture_pus_only      = _g(f'culture_pus_only_{item.id}')
    r.culture_growth_1      = _g(f'culture_growth_1_{item.id}')
    r.culture_growth_2      = _g(f'culture_growth_2_{item.id}')
    r.culture_growth_3      = _g(f'culture_growth_3_{item.id}')
    r.culture_colony_1      = _g(f'culture_colony_1_{item.id}')
    r.culture_colony_2      = _g(f'culture_colony_2_{item.id}')
    r.culture_colony_3      = _g(f'culture_colony_3_{item.id}')
    r.culture_micro_text    = _g(f'culture_microscopy_text_{item.id}')
    r.culture_micro_note    = _g(f'culture_microscopy_note_{item.id}')
    r.culture_direct_text   = _g(f'culture_direct_text_{item.id}')
    r.culture_direct_note   = _g(f'culture_direct_note_{item.id}')
    r.culture_zn_text       = _g(f'culture_zn_text_{item.id}')
    r.culture_zn_note       = _g(f'culture_zn_note_{item.id}')
    r.culture_gram_text     = _g(f'culture_gram_text_{item.id}')
    r.culture_gram_note     = _g(f'culture_gram_note_{item.id}')
    r.culture_comments_dd   = _g(f'culture_comments_dd_{item.id}')
    r.culture_comments_txt  = _g(f'culture_comments_txt_{item.id}')

    # Bacteria ? multi-select
    bacteria_ids = form.getlist(f'culture_bacteria_{item.id}')
    r.culture_bacteria_ids = ','.join(bacteria_ids) if bacteria_ids else None

    r.entered_at = datetime.utcnow()
    if user is not None:
        r.entered_by_id = getattr(user, 'id', None)
    # Antibiotic grid
    ab_values = {}
    pat = re.compile(r"^ca_(mic_[123]|s_[123])_(\d+)_(\d+)$")
    for key in form:
        m = pat.match(key)
        if not m:
            continue
        field, item_part, ab_id = m.group(1), int(m.group(2)), int(m.group(3))
        if item_part != item.id:
            continue
        ab_values.setdefault(ab_id, {})[field] = (form.get(key) or "").strip() or None



    for ab_id, vals in ab_values.items():
        row = CultureAntibiotic.query.filter_by(
            order_item_id=item.id, antibiotic_id=ab_id).first()
        if row is None:
            row = CultureAntibiotic(order_item_id=item.id, antibiotic_id=ab_id)
            db.session.add(row)
        for k in ('mic_1','s_1','mic_2','s_2','mic_3','s_3'):
            setattr(row, k, vals.get(k))

    # also save the short "value" so the item counts as filled
    item.result_value = r.culture_specimen or 'Culture'
    db.session.commit()
    return r

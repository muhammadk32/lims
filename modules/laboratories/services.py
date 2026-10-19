"""Laboratory services — auto-create rate list for a lab."""
def sync_lab_rate_list(lab, force=False):
    """Ensure the lab has its own rate list, populated from Standard."""
    from extensions import db
    from modules.tests.models import (
        RateCategory, RateCategoryTest, RateCategoryDeptRate,
        TestCategory, PanelParameter, Test,
    )

    if lab.rate_category_id and not force:
        return lab.rate_category

    std = (RateCategory.query.filter_by(is_standard=True).first()
           or RateCategory.query.filter(RateCategory.name == 'Standard Rate List').first())
    if not std:
        return None

    auto_name = f'{lab.name} rate'
    existing = RateCategory.query.filter_by(name=auto_name).first()
    if existing:
        # clean out any existing test rows and re-seed from std canonical
        RateCategoryTest.query.filter_by(rate_category_id=existing.id).delete(synchronize_session=False)
        db.session.commit()
        cat = existing
    else:
        cat = RateCategory(
            name=auto_name,
            description=f'Auto-created for {lab.name}',
            parent_rate_category_id=std.id,
            is_standard=False,
            is_active=True,
        )
        db.session.add(cat)
        db.session.commit()

    # ---- build canonical test id list (fetch before any add) ----
    child_ids = {r[0] for r in
                 db.session.query(PanelParameter.test_id).distinct().all()}
    active_ids = {r[0] for r in
                  db.session.query(Test.id).filter(Test.is_active == True).all()}
    std_ids_raw = [r[0] for r in
                   db.session.query(RateCategoryTest.test_id)
                   .filter_by(rate_category_id=std.id)
                   .order_by(RateCategoryTest.sort_order.asc()).all()]

    canonical_ids = []
    seen = set()
    for tid in std_ids_raw:
        if tid in seen: continue
        if tid in child_ids: continue
        if tid not in active_ids: continue
        seen.add(tid)
        canonical_ids.append(tid)

    # ---- insert test rows (dedup guaranteed) ----
    existing_test_ids = {r[0] for r in
                         db.session.query(RateCategoryTest.test_id)
                         .filter_by(rate_category_id=cat.id).all()}
    sort_i = 0
    for tid in canonical_ids:
        if tid in existing_test_ids:
            continue
        sort_i += 1
        db.session.add(RateCategoryTest(
            rate_category_id=cat.id,
            test_id=tid,
            sort_order=sort_i,
        ))
    db.session.commit()

    # ---- seed dept rates (dedup) ----
    default_pct = float(lab.discount_percent or 0)
    default_comm = float(lab.commission_percent or 0)
    existing_depts = {r[0] for r in
                      db.session.query(RateCategoryDeptRate.department_id)
                      .filter_by(rate_category_id=cat.id).all()}
    for dept in TestCategory.query.all():
        if dept.id in existing_depts:
            continue
        db.session.add(RateCategoryDeptRate(
            rate_category_id=cat.id,
            department_id=dept.id,
            discount_percent=default_pct,
            commission_percent=default_comm,
        ))
    db.session.commit()

    lab.rate_category_id = cat.id
    db.session.commit()
    return cat

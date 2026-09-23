"""Patient queries."""


# ============================================================
# Search patients + their visit history
# ============================================================
def search_patients_with_visits(q='', limit=50):
    """Return (patients, visits_by_patient_id).

    Searches by phone, name, or patient_code.
    Each patient's visits include: order, tests, totals, status.
    """
    from modules.patients.models import Patient
    from modules.orders.models import Order, OrderStatus

    query = Patient.query

    if q:
        like = f'%{q}%'
        from sqlalchemy import or_
        query = query.filter(or_(
            Patient.phone.ilike(like),
            Patient.full_name.ilike(like),
            Patient.patient_code.ilike(like),
        ))

    patients = query.order_by(Patient.id.desc()).limit(limit).all()

    visits = {}
    for p in patients:
        orders = (
            Order.query
            .filter(Order.patient_id == p.id)
            .order_by(Order.id.desc())
            .all()
        )
        visits[p.id] = orders

    return patients, visits

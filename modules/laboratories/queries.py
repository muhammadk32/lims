"""Query helpers for laboratories."""
from extensions import db
from .models import Laboratory


def search_laboratories(query, limit=10):
    """Typeahead search — matches name, contact, phone."""
    q = (query or '').strip()
    base = Laboratory.query.filter(Laboratory.is_active == True)  # noqa: E712
    if q:
        like = f'%{q}%'
        base = base.filter(
            db.or_(
                Laboratory.name.ilike(like),
                Laboratory.contact_person.ilike(like),
                Laboratory.phone.ilike(like),
            )
        )
    return (base.order_by(Laboratory.times_used.desc(),
                          Laboratory.name.asc())
                .limit(limit)
                .all())


def get_laboratory(lab_id):
    if not lab_id:
        return None
    return Laboratory.query.get(lab_id)

"""Business logic for referral suggestions."""
from datetime import datetime

from sqlalchemy import func

from extensions import db
from .models import Referral


def upsert_referral(name, clinic=None, phone=None):
    """Create or bump a referral suggestion.

    Returns the Referral row, or None if name is empty.
    """
    name = (name or '').strip()
    if not name:
        return None

    # Case-insensitive match
    existing = (
        Referral.query
        .filter(func.lower(Referral.name) == name.lower())
        .first()
    )

    now = datetime.utcnow()

    if existing:
        existing.times_used = (existing.times_used or 0) + 1
        existing.last_used_at = now
        if clinic and not existing.clinic:
            existing.clinic = clinic
        if phone and not existing.phone:
            existing.phone = phone
        db.session.flush()
        return existing

    ref = Referral(
        name=name,
        clinic=(clinic or None),
        phone=(phone or None),
        times_used=1,
        last_used_at=now,
    )
    db.session.add(ref)
    db.session.flush()
    return ref

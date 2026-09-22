"""Query helpers for referral suggestions."""
from .models import Referral


def search_referrals(q, limit=8):
    """Return referral suggestions matching q.

    Ranking: most-used first, then most-recent, then alphabetical.
    """
    if not q or len(q) < 2:
        return []

    like = f'%{q}%'
    return (
        Referral.query
        .filter(Referral.name.ilike(like))
        .order_by(
            Referral.times_used.desc(),
            Referral.last_used_at.desc().nullslast(),
            Referral.name.asc(),
        )
        .limit(limit)
        .all()
    )

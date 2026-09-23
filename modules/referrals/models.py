"""Referral model — stores suggestion names for the typeahead.

Not a foreign key target. Orders store their own referred_by_name string.
"""
from extensions import db
from core.models import BaseModel


class Referral(BaseModel):
    __tablename__ = 'referrals'

    name = db.Column(db.String(120), nullable=False, unique=True, index=True)
    clinic = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(30), nullable=True)

    # Commission percent (0-100). E.g. 20.0 = 20%% of final total.
    commission_percent = db.Column(db.Float, nullable=False, default=0.0)

    # Usage counters — help rank suggestions
    times_used = db.Column(db.Integer, nullable=False, default=1)
    last_used_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<Referral {self.name} ({self.times_used}x)>'

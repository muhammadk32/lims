"""Laboratory model — external labs / companies that refer patients.

Not a FK target on orders — orders snapshot `company_name` so the
printed record stays stable even if the laboratory is renamed later.
"""
from extensions import db
from core.models import BaseModel


class Laboratory(BaseModel):
    __tablename__ = 'laboratories'

    name = db.Column(db.String(150), nullable=False, unique=True, index=True)
    contact_person = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    # Discount percent to apply automatically (0-100).
    discount_percent = db.Column(db.Float, nullable=False, default=0.0)

    # Commission percent paid back to the lab (0-100).
    commission_percent = db.Column(db.Float, nullable=False, default=0.0)

    is_active = db.Column(db.Boolean, nullable=False, default=True)
    times_used = db.Column(db.Integer, nullable=False, default=0)
    last_used_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<Laboratory {self.name} discount={self.discount_percent}%>'

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

    # ---------- Outsourced / partner-lab fields ----------
    # True means: we send our outsourced tests TO this lab.
    # False means: this lab refers patients TO us (referrer company).
    # Both kinds live in this table; is_partner_lab distinguishes them.
    is_partner_lab = db.Column(db.Boolean, nullable=False, default=False, index=True)

    # Cap on discount for outsourced tests assigned to this lab.
    # NULL = no cap. Pre-fills the test form when assigning.
    default_max_discount_percent = db.Column(db.Float, nullable=True)

    is_active = db.Column(db.Boolean, nullable=False, default=True)

    # Default rate category (rate list) for this lab/company
    rate_category_id = db.Column(
        db.Integer,
        db.ForeignKey('rate_categories.id'),
        nullable=True,
        index=True,
    )
    rate_category = db.relationship('RateCategory', foreign_keys=[rate_category_id])
    times_used = db.Column(db.Integer, nullable=False, default=0)
    last_used_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<Laboratory {self.name} discount={self.discount_percent}%>'

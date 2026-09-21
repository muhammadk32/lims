from extensions import db
from core.models import BaseModel
from datetime import datetime


class PaymentMethod:
    CASH = 'cash'
    CARD = 'card'
    BANK = 'bank'
    INSURANCE = 'insurance'
    MOBILE = 'mobile'
    OTHER = 'other'

    CHOICES = [CASH, CARD, BANK, INSURANCE, MOBILE, OTHER]

    LABELS = {
        CASH: 'Cash',
        CARD: 'Card',
        BANK: 'Bank Transfer',
        INSURANCE: 'Insurance',
        MOBILE: 'Mobile Wallet',
        OTHER: 'Other',
    }


class Payment(BaseModel):
    __tablename__ = 'payments'

    order_id = db.Column(
        db.Integer,
        db.ForeignKey('orders.id'),
        nullable=False,
        index=True
    )

    amount = db.Column(db.Float, nullable=False, default=0.0)
    method = db.Column(db.String(20), default=PaymentMethod.CASH, nullable=False)
    reference = db.Column(db.String(80), nullable=True)   # transaction ID
    notes = db.Column(db.String(255), nullable=True)

    received_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Relationships
    order = db.relationship('Order', backref=db.backref('payments', lazy='select', cascade='all, delete-orphan'))
    received_by = db.relationship('User', foreign_keys=[received_by_id])

    @property
    def method_label(self):
        return PaymentMethod.LABELS.get(self.method, self.method.capitalize())

    def __repr__(self):
        return f'<Payment ${self.amount:.2f} ({self.method}) order={self.order_id}>'
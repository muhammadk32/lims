from datetime import datetime
from extensions import db


class Result(db.Model):
    __tablename__ = 'results'

    id = db.Column(db.Integer, primary_key=True)
    order_item_id = db.Column(
        db.Integer,
        db.ForeignKey('order_items.id'),
        nullable=False,
        unique=True
    )
    value = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    entered_by_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=True
    )
    entered_at = db.Column(db.DateTime, default=datetime.utcnow)

    order_item = db.relationship('OrderItem', backref='result')
    entered_by = db.relationship('User')

    def __repr__(self):
        return f'<Result item={self.order_item_id} value={self.value!r}>'
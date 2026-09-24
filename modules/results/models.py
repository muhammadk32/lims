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

    # ---------- PCR-style extended fields (ADAM layout) ----------
    specimen           = db.Column(db.String(120), nullable=True)
    result_type        = db.Column(db.String(40),  nullable=True)
    viral_load_type    = db.Column(db.String(80),  nullable=True)
    no_of_repeat       = db.Column(db.Integer,     nullable=True)
    method_html        = db.Column(db.Text,        nullable=True)
    suggestion_html    = db.Column(db.Text,        nullable=True)
    interpretation_html= db.Column(db.Text,        nullable=True)
    comments_html      = db.Column(db.Text,        nullable=True)
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
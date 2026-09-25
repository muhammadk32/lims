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

    # ---------- Culture & Sensitivity fields ----------
    culture_specimen      = db.Column(db.String(120), nullable=True)
    culture_no_sensitive  = db.Column(db.String(40),  nullable=True)
    culture_bacteria_ids  = db.Column(db.Text,        nullable=True)   # JSON list of Bacterium ids
    culture_phage_name    = db.Column(db.Text,        nullable=True)
    culture_pus_only      = db.Column(db.String(40),  nullable=True)
    culture_growth_1      = db.Column(db.Text,        nullable=True)
    culture_growth_2      = db.Column(db.Text,        nullable=True)
    culture_growth_3      = db.Column(db.Text,        nullable=True)
    culture_colony_1      = db.Column(db.String(40),  nullable=True)
    culture_colony_2      = db.Column(db.String(40),  nullable=True)
    culture_colony_3      = db.Column(db.String(40),  nullable=True)
    # Culture Growth tab
    culture_micro_text    = db.Column(db.String(120), nullable=True)
    culture_micro_note    = db.Column(db.Text,        nullable=True)
    culture_direct_text   = db.Column(db.String(120), nullable=True)
    culture_direct_note   = db.Column(db.Text,        nullable=True)
    culture_zn_text       = db.Column(db.String(120), nullable=True)
    culture_zn_note       = db.Column(db.Text,        nullable=True)
    culture_gram_text     = db.Column(db.String(120), nullable=True)
    culture_gram_note     = db.Column(db.Text,        nullable=True)
    # Comments tab
    culture_comments_dd   = db.Column(db.String(80),  nullable=True)
    culture_comments_txt  = db.Column(db.Text,        nullable=True)
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
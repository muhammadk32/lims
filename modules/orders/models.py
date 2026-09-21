# modules/orders/models.py
from extensions import db
from core.models import BaseModel
from datetime import datetime


class OrderStatus:
    PENDING     = 'pending'
    COLLECTED   = 'collected'
    COMPLETED   = 'completed'
    APPROVED    = 'approved'
    CORRECTION  = 'correction'
    CANCELLED   = 'cancelled'

    CHOICES = [PENDING, COLLECTED, COMPLETED, APPROVED, CORRECTION, CANCELLED]

    LABELS = {
        PENDING:    'Pending',
        COLLECTED:  'Collected',
        COMPLETED:  'Completed',
        APPROVED:   'Approved',
        CORRECTION: 'Correction',
        CANCELLED:  'Cancelled',
    }


class Order(BaseModel):
    __tablename__ = 'orders'

    order_code = db.Column(db.String(20), unique=True, nullable=False, index=True)

    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False, index=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    total_amount = db.Column(db.Float, default=0.0, nullable=False)
    paid = db.Column(db.Boolean, default=False, nullable=False)
    status = db.Column(db.String(20), default=OrderStatus.PENDING, nullable=False, index=True)

    discount_type = db.Column(db.String(10), default='amount', nullable=False)
    discount_amount = db.Column(db.Float, default=0.0, nullable=False)
    discount_percent = db.Column(db.Float, default=0.0, nullable=False)
    discount_reason = db.Column(db.String(255), nullable=True)

    sample_collected_at = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    # Order-level approval (kept for backward compat — but the source of
    # truth is now per-item verification)
    reported_at = db.Column(db.DateTime, nullable=True)
    reported_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    correction_note = db.Column(db.Text, nullable=True)
    correction_at = db.Column(db.DateTime, nullable=True)
    correction_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    patient = db.relationship('Patient', backref='orders')
    doctor = db.relationship('User', foreign_keys=[doctor_id], backref='orders')
    reported_by = db.relationship('User', foreign_keys=[reported_by_id])
    correction_by = db.relationship('User', foreign_keys=[correction_by_id])

    items = db.relationship(
        'OrderItem',
        backref='order',
        cascade='all, delete-orphan',
        lazy='select',
    )

    # ---------- Item helpers ----------
    @property
    def item_count(self):
        return len(self.items)

    @property
    def top_level_items(self):
        return [i for i in self.items if i.parent_item_id is None]

    @property
    def standalone_items(self):
        return [i for i in self.top_level_items if not i.has_children]

    @property
    def panel_items(self):
        return [i for i in self.top_level_items if i.has_children]

    @property
    def panel_count(self):
        return len(self.panel_items)

    @property
    def standalone_count(self):
        return len(self.standalone_items)

    @property
    def billable_item_count(self):
        return len(self.top_level_items)

    @property
    def all_display_items(self):
        result = []
        for item in self.top_level_items:
            result.append(item)
            for child in item.children:
                result.append(child)
        return result

    # ---------- Result progress ----------
    @property
    def all_results_done(self):
        """True if every leaf test has a result."""
        top = self.top_level_items
        if not top:
            return False

        for item in top:
            if item.has_children:
                if not all(c.result_value for c in item.children):
                    return False
            else:
                if not item.result_value:
                    return False

        return True

    # ---------- Verification helpers (per top-level item) ----------
    @property
    def verifiable_items(self):
        """Top-level items with a result entered and awaiting verification.

        A panel is 'verifiable' when every child has a result.
        A standalone test is 'verifiable' when its own result is set.
        """
        result = []
        for item in self.top_level_items:
            if item.is_verifiable:
                result.append(item)
        return result

    @property
    def verified_items(self):
        """Top-level items already verified by a pathologist."""
        return [i for i in self.top_level_items if i.is_verified]

    @property
    def has_verified_items(self):
        return len(self.verified_items) > 0

    @property
    def pending_verification_items(self):
        """Items with a result but not yet verified."""
        return [i for i in self.top_level_items
                if i.is_verifiable and not i.is_verified]

    @property
    def all_verified(self):
        """True if every top-level item is verified."""
        top = self.top_level_items
        if not top:
            return False
        return all(i.is_verified for i in top)

    @property
    def partially_verified(self):
        """True if some (but not all) top-level items are verified."""
        return self.has_verified_items and not self.all_verified

    # ---------- Approval state ----------
    @property
    def is_approved(self):
        """True only when the whole order is verified."""
        return self.all_verified and self.status == OrderStatus.APPROVED

    @property
    def needs_correction(self):
        return self.status == OrderStatus.CORRECTION

    @property
    def status_label(self):
        return OrderStatus.LABELS.get(self.status, self.status.capitalize())

    # ---------- Financial helpers ----------
    def recompute_total(self):
        self.total_amount = sum((i.price or 0.0) for i in self.top_level_items)
        return self.total_amount

    @property
    def subtotal(self):
        return sum((i.price or 0.0) for i in self.top_level_items)

    @property
    def discount_value(self):
        if self.discount_type == 'percent':
            pct = max(0.0, min(100.0, self.discount_percent or 0.0))
            return round(self.subtotal * (pct / 100.0), 2)
        return round(max(0.0, self.discount_amount or 0.0), 2)

    @property
    def final_total(self):
        return max(0.0, round(self.subtotal - self.discount_value, 2))

    @property
    def paid_amount(self):
        return sum((p.amount or 0.0) for p in self.payments)

    @property
    def balance_due(self):
        return max(0.0, self.final_total - self.paid_amount)

    @property
    def is_fully_paid(self):
        return self.balance_due <= 0.001

    @property
    def payment_status(self):
        if self.paid_amount <= 0.001:
            return 'unpaid'
        if self.is_fully_paid:
            return 'paid'
        return 'partial'

    def __repr__(self):
        return f'<Order {self.order_code} ({self.status})>'


class OrderItem(BaseModel):
    __tablename__ = 'order_items'

    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, index=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False)

    price = db.Column(db.Float, default=0.0, nullable=False)

    parent_item_id = db.Column(
        db.Integer,
        db.ForeignKey('order_items.id', ondelete='CASCADE'),
        nullable=True,
        index=True,
    )
    sort_order = db.Column(db.Integer, default=0, nullable=False)

    result_value = db.Column(db.String(200), nullable=True)
    result_notes = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='pending', nullable=False)

    # ---------- Per-item verification (NEW) ----------
    verified_at = db.Column(db.DateTime, nullable=True)
    verified_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Per-item correction note (NEW) — pathologist sends back a specific test
    correction_note = db.Column(db.Text, nullable=True)
    correction_at = db.Column(db.DateTime, nullable=True)
    correction_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    test = db.relationship('Test')
    verified_by = db.relationship('User', foreign_keys=[verified_by_id])
    correction_by = db.relationship('User', foreign_keys=[correction_by_id])

    children = db.relationship(
        'OrderItem',
        backref=db.backref('parent', remote_side='OrderItem.id'),
        cascade='all, delete-orphan',
        order_by='OrderItem.sort_order',
        single_parent=True,
    )

    @property
    def is_child(self):
        return self.parent_item_id is not None

    @property
    def is_parent(self):
        return self.parent_item_id is None and len(self.children) > 0

    @property
    def has_children(self):
        return len(self.children) > 0

    @property
    def is_billable(self):
        return self.parent_item_id is None

    @property
    def is_panel(self):
        return bool(self.test and self.test.is_panel)

    # ---------- Result completeness ----------
    @property
    def all_children_have_results(self):
        if not self.has_children:
            return False
        return all(c.result_value for c in self.children)

    @property
    def has_result(self):
        """True if this item (or every child, for a panel) has a result."""
        if self.has_children:
            return self.all_children_have_results
        return bool(self.result_value)

    # ---------- Verification state ----------
    @property
    def is_verified(self):
        """True only for top-level items verified by a pathologist.

        Panel children are never verified individually — only the
        top-level panel is. A standalone top-level test verifies itself.
        """
        if self.is_child:
            return False
        return self.verified_at is not None

    @property
    def is_verifiable(self):
        """True if this item has a result and could be verified.

        - Panel: all children have results
        - Standalone: own result_value is set
        """
        if self.is_child:
            return False
        return self.has_result

    @property
    def needs_correction(self):
        """True if the pathologist sent this specific item back."""
        return bool(self.correction_note) and not self.is_verified

    def __repr__(self):
        kind = 'CHILD' if self.is_child else 'TOP'
        return f'<OrderItem {kind} test={self.test_id} price={self.price}>'
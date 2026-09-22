from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


class BaseModel(db.Model):
    """
    Abstract base class for all models.
    Provides: id, created_at, updated_at.
    Every future model will inherit from this.
    """
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )


class User(BaseModel, UserMixin):
    """
    User accounts for the system.
    Roles: admin, doctor, technician
    """
    __tablename__ = 'users'

    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    role = db.Column(db.String(20), default='technician', nullable=False)
    is_active_flag = db.Column(db.Boolean, default=True, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)

    # ---------- User preferences ----------
    theme = db.Column(db.String(30), nullable=False, default='light')

    # ---------- Password helpers ----------
    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    # ---------- Flask-Login requirement ----------
    @property
    def is_active(self):
        return self.is_active_flag

    # ---------- Convenience ----------
    def has_role(self, *roles) -> bool:
        return self.role in roles

    @property
    def role_label(self):
        from core.roles import Role
        return Role.LABELS.get(self.role, self.role.capitalize())

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


class AuditLog(db.Model):
    """
    Records every important action for compliance & debugging.
    """
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    username = db.Column(db.String(80), nullable=True)

    action = db.Column(db.String(50), nullable=False, index=True)
    entity = db.Column(db.String(50), nullable=False, index=True)
    entity_id = db.Column(db.Integer, nullable=True)

    summary = db.Column(db.String(255), nullable=True)
    extra = db.Column(db.Text, nullable=True)

    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)

    user = db.relationship('User', foreign_keys=[user_id])

    def __repr__(self):
        return f'<AuditLog {self.action} {self.entity}#{self.entity_id} by {self.username}>'


# ============================================================
# LAB SETTINGS â€” Branding & Contact Info (Singleton)
# ============================================================
class LabSettings(BaseModel):
    """
    Singleton table â€” only ever holds ONE row (id=1).
    Stores branding + contact details shown across the app and printed reports.
    """
    __tablename__ = 'lab_settings'

    # --- Branding ---
    lab_name = db.Column(db.String(150), nullable=False,
                         default='Laboratory Management System')
    tagline = db.Column(db.String(200), nullable=True, default='')
    logo_filename = db.Column(db.String(255), nullable=True)

    # --- Contact / Print header ---
    address = db.Column(db.String(255), nullable=True, default='')
    phone = db.Column(db.String(50), nullable=True, default='')
    email = db.Column(db.String(120), nullable=True, default='')
    website = db.Column(db.String(150), nullable=True, default='')
    license_no = db.Column(db.String(80), nullable=True, default='')

    # --- Print footer ---
    footer_note = db.Column(db.String(255), nullable=True,
                            default='Thank you for choosing our lab.')

    # --- Theme color ---
    primary_color = db.Column(db.String(20), nullable=False, default='#0d6efd')

    # --- Currency ---
    currency_symbol = db.Column(db.String(10), nullable=False, default='Rs')

    # ---------- Helpers ----------
    @classmethod
    def get(cls):
        obj = cls.query.first()
        if not obj:
            obj = cls()
            db.session.add(obj)
            db.session.commit()
        return obj

    @property
    def logo_url(self):
        if not self.logo_filename:
            return None
        from flask import url_for
        return url_for('static', filename=f'uploads/branding/{self.logo_filename}')

    def __repr__(self):
        return f'<LabSettings {self.lab_name!r}>'


# ============================================================
# FORM FIELD CONFIG â€” Reception form customization
# ============================================================
class FormFieldConfig(BaseModel):
    """
    Per-field configuration for the reception/order form.
    Each row corresponds to one field in `core.form_fields.FORM_FIELDS`.
    """
    __tablename__ = 'form_field_configs'

    field_key = db.Column(db.String(50), unique=True, nullable=False, index=True)
    section = db.Column(db.String(30), nullable=False, index=True)

    is_visible = db.Column(db.Boolean, default=False, nullable=False)
    is_required = db.Column(db.Boolean, default=False, nullable=False)

    default_value = db.Column(db.String(255), nullable=True)
    custom_label = db.Column(db.String(80), nullable=True)
    help_text = db.Column(db.String(255), nullable=True)

    sort_order = db.Column(db.Integer, default=0, nullable=False)

    # ---------- Helpers ----------
    @classmethod
    def get(cls, field_key):
        return cls.query.filter_by(field_key=field_key).first()

    @classmethod
    def as_dict(cls):
        return {c.field_key: c for c in cls.query.all()}

    def __repr__(self):
        return f'<FormFieldConfig {self.field_key} vis={self.is_visible} req={self.is_required}>'


# ============================================================
# FORM SECTION CONFIG â€” toggle whole sections on/off
# ============================================================
class FormSectionConfig(BaseModel):
    """
    Per-section toggle for the reception form.
    """
    __tablename__ = 'form_section_configs'

    section_key = db.Column(db.String(30), unique=True, nullable=False, index=True)
    is_visible = db.Column(db.Boolean, default=True, nullable=False)
    sort_order = db.Column(db.Integer, default=0, nullable=False)

    @classmethod
    def as_dict(cls):
        return {c.section_key: c for c in cls.query.all()}

    def __repr__(self):
        return f'<FormSectionConfig {self.section_key} vis={self.is_visible}>'
# ============================================================
# REPORT SIGNATURES â€” doctors/staff panel on printed reports
# ============================================================
class ReportSignature(BaseModel):
    """
    A single entry in the signature panel printed at the bottom
    of result reports. Layout: 4 per row, in sort_order.
    """
    __tablename__ = 'report_signatures'

    name = db.Column(db.String(120), nullable=False)
    qualifications = db.Column(db.String(255), nullable=True)
    designation = db.Column(db.String(120), nullable=True)
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    @classmethod
    def active_ordered(cls):
        return (
            cls.query
            .filter_by(is_active=True)
            .order_by(cls.sort_order, cls.id)
            .all()
        )

    def __repr__(self):
        return f'<ReportSignature {self.name}>'

# Import Referral so it's registered with SQLAlchemy metadata
from modules.referrals.models import Referral  # noqa: F401,E402


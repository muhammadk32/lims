from extensions import db
from core.models import BaseModel
from datetime import date


class Patient(BaseModel):
    __tablename__ = 'patients'

    # Auto-generated code like P20250115143022
    patient_code = db.Column(db.String(20), unique=True, nullable=False, index=True)

    # Personal info
    full_name = db.Column(db.String(120), nullable=False, index=True)
    age = db.Column(db.Integer, nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=True)   # Male / Female / Other

    # Contact
    phone = db.Column(db.String(30), nullable=True, index=True)
    email = db.Column(db.String(120), nullable=True)
    address = db.Column(db.Text, nullable=True)

    # Extra
    blood_group = db.Column(db.String(5), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # ---------- Helpers ----------
    def compute_age(self):
        """If DOB is set, compute age automatically."""
        if self.date_of_birth:
            today = date.today()
            return (
                today.year
                - self.date_of_birth.year
                - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
            )
        return self.age

    def __repr__(self):
        return f'<Patient {self.patient_code} — {self.full_name}>'
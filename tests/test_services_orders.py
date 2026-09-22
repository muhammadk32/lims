"""Tests for modules/orders/services.py — no HTTP."""
import uuid
import pytest
from datetime import datetime

from extensions import db
from modules.orders.models import Order, OrderItem, OrderStatus
from modules.orders import services as svc
from modules.orders import queries as q
from core.models import User


def _u():
    return uuid.uuid4().hex[:8].upper()


def _get_user(username):
    return User.query.filter_by(username=username).first()


def _make_test(**kw):
    from modules.tests.models import Test
    defaults = dict(
        code=f'TS{_u()}', name=f'Test {_u()}', price=10.0,
        unit='u', normal_range='1 - 10',
        is_active=True, is_panel=False,
    )
    defaults.update(kw)
    t = Test(**defaults)
    db.session.add(t)
    db.session.flush()
    return t


def _make_patient(**kw):
    from modules.patients.models import Patient
    defaults = dict(patient_code=f'P{_u()}', full_name=f'Patient {_u()}')
    defaults.update(kw)
    p = Patient(**defaults)
    db.session.add(p)
    db.session.flush()
    return p


class FakeForm:
    """Minimal form-like object that mimics request.form."""
    def __init__(self, data=None, lists=None):
        self.data = data or {}
        self.lists = lists or {}

    def get(self, key, default=None, type=None):
        v = self.data.get(key, default)
        if v is None:
            return default
        if type is not None:
            try:
                return type(v)
            except (ValueError, TypeError):
                return default
        return v

    def getlist(self, key, type=None):
        vals = self.lists.get(key, [])
        if type is not None:
            out = []
            for v in vals:
                try:
                    out.append(type(v))
                except (ValueError, TypeError):
                    pass
            return out
        return vals


# ============================================================
# Code generators
# ============================================================
def test_generate_order_code_format(app):
    with app.app_context():
        code = q.generate_order_code()
        parts = code.split('-')
        assert len(parts) == 2
        assert parts[0].isdigit() and len(parts[0]) == 4
        assert parts[1].isdigit() and int(parts[1]) >= 1


def test_generate_patient_code_format(app):
    with app.app_context():
        code = q.generate_patient_code()
        assert code.startswith('P')
        assert code[1:].isdigit()
        assert len(code) == 6


# ============================================================
# create_patient
# ============================================================
def test_create_patient_success(app):
    with app.app_context():
        form = FakeForm({'patient_name': 'Alice Test', 'age_value': '25',
                         'age_unit': 'years', 'gender': 'Female'})
        patient = svc.create_patient(form)
        assert patient.id
        assert patient.full_name == 'Alice Test'
        assert patient.age == 25


def test_create_patient_missing_name_raises(app):
    with app.app_context():
        form = FakeForm({})
        with pytest.raises(ValueError, match='Patient name'):
            svc.create_patient(form)


def test_create_patient_age_in_months(app):
    with app.app_context():
        form = FakeForm({'patient_name': 'Baby', 'age_value': '6',
                         'age_unit': 'months'})
        patient = svc.create_patient(form)
        assert patient.age in (0, 1)


# ============================================================
# create_order
# ============================================================
def test_create_order_simple(app):
    with app.app_context():
        patient = _make_patient()
        t = _make_test(code=f'SIMPLE{_u()}', name='Simple', price=12.5)
        user = _get_user('admin')

        form = FakeForm({'payment_amount': '0'})
        order = svc.create_order(patient, [t], form, user)

        assert order.id
        assert order.status == OrderStatus.PENDING
        assert order.item_count == 1
        assert order.final_total == 12.5


def test_create_order_with_panel(app):
    with app.app_context():
        from modules.tests.models import Test, PanelParameter

        patient = _make_patient()
        panel = Test(code=f'PNL{_u()}', name='Panel', price=20.0,
                     is_panel=True, is_active=True)
        db.session.add(panel)
        db.session.flush()
        c1 = _make_test(code=f'C1{_u()}', name='Child 1', price=0.0)
        c2 = _make_test(code=f'C2{_u()}', name='Child 2', price=0.0)
        db.session.add(PanelParameter(panel_id=panel.id, test_id=c1.id, sort_order=0))
        db.session.add(PanelParameter(panel_id=panel.id, test_id=c2.id, sort_order=1))
        db.session.flush()

        user = _get_user('admin')
        form = FakeForm({'payment_amount': '0'})
        order = svc.create_order(patient, [panel], form, user)

        assert order.item_count == 3
        assert order.final_total == 20.0
        assert order.panel_count == 1


def test_create_order_with_payment(app):
    with app.app_context():
        patient = _make_patient()
        t = _make_test(code=f'PAID{_u()}', name='Paid', price=100.0)
        user = _get_user('admin')
        form = FakeForm({'payment_amount': '60', 'payment_method': 'cash'})
        order = svc.create_order(patient, [t], form, user)

        assert order.paid_amount == 60.0
        assert order.final_total == 100.0
        assert order.paid is False


def test_create_order_full_payment_marks_paid(app):
    with app.app_context():
        patient = _make_patient()
        t = _make_test(code=f'FULL{_u()}', name='Full', price=50.0)
        user = _get_user('admin')
        form = FakeForm({'payment_amount': '50', 'payment_method': 'cash'})
        order = svc.create_order(patient, [t], form, user)
        assert order.paid is True


def test_create_order_with_discount_amount(app):
    with app.app_context():
        patient = _make_patient()
        t = _make_test(code=f'DISC{_u()}', name='Disc', price=100.0)
        user = _get_user('admin')
        form = FakeForm({
            'discount_type': 'amount',
            'discount_amount': '15',
            'payment_amount': '0',
        })
        order = svc.create_order(patient, [t], form, user)
        assert order.final_total == 85.0


def test_create_order_with_discount_percent(app):
    with app.app_context():
        patient = _make_patient()
        t = _make_test(code=f'DISC{_u()}', name='PctDisc', price=200.0)
        user = _get_user('admin')
        form = FakeForm({
            'discount_type': 'percent',
            'discount_percent': '25',
            'payment_amount': '0',
        })
        order = svc.create_order(patient, [t], form, user)
        assert order.final_total == 150.0


# ============================================================
# Status transitions
# ============================================================
def test_change_order_status_valid(app):
    with app.app_context():
        patient = _make_patient()
        t = _make_test(code=f'ST{_u()}', name='St', price=5.0)
        user = _get_user('admin')
        order = svc.create_order(patient, [t], FakeForm({'payment_amount': '0'}), user)

        ok = svc.change_order_status(order, OrderStatus.COLLECTED, user)
        assert ok is True
        assert order.status == OrderStatus.COLLECTED
        assert order.sample_collected_at is not None


def test_change_order_status_invalid(app):
    with app.app_context():
        patient = _make_patient()
        t = _make_test(code=f'ST{_u()}', name='St2', price=5.0)
        user = _get_user('admin')
        order = svc.create_order(patient, [t], FakeForm({'payment_amount': '0'}), user)

        ok = svc.change_order_status(order, 'nonsense_status', user)
        assert ok is False
        assert order.status == OrderStatus.PENDING


# ============================================================
# Approval / send-back
# ============================================================
def test_can_approve_roles(app):
    with app.app_context():
        admin = _get_user('admin')
        doctor = _get_user('doctor')
        tech = _get_user('tech')
        assert svc.can_approve(admin) is True
        assert svc.can_approve(doctor) is True
        assert svc.can_approve(tech) is False


def test_approve_order_wrong_status(app):
    """Order is PENDING, not COMPLETED/CORRECTION — should be rejected."""
    with app.app_context():
        patient = _make_patient()
        t = _make_test(code=f'APP{_u()}', name='App', price=5.0)
        user = _get_user('admin')
        order = svc.create_order(patient, [t], FakeForm({'payment_amount': '0'}), user)

        ok, err = svc.approve_order(order, user)
        assert ok is False
        assert 'completed' in err.lower() or 'correction' in err.lower()


def test_approve_order_requires_all_results(app):
    """Order is COMPLETED but has no result values — should be rejected."""
    with app.app_context():
        patient = _make_patient()
        t = _make_test(code=f'APP{_u()}', name='AppNoResult', price=5.0)
        user = _get_user('admin')
        order = svc.create_order(patient, [t], FakeForm({'payment_amount': '0'}), user)
        order.status = OrderStatus.COMPLETED
        db.session.commit()

        ok, err = svc.approve_order(order, user)
        assert ok is False
        assert 'missing' in err.lower()


def test_approve_order_success(app):
    with app.app_context():
        patient = _make_patient()
        t = _make_test(code=f'APPOK{_u()}', name='AppOK', price=5.0)
        user = _get_user('admin')
        order = svc.create_order(patient, [t], FakeForm({'payment_amount': '0'}), user)

        item = order.top_level_items[0]
        item.result_value = '5'
        order.status = OrderStatus.COMPLETED
        db.session.commit()

        ok, err = svc.approve_order(order, user)
        assert ok is True, err
        assert order.status == OrderStatus.APPROVED
        assert order.reported_at is not None


def test_send_back_requires_reason(app):
    with app.app_context():
        patient = _make_patient()
        t = _make_test(code=f'SB{_u()}', name='SB1', price=5.0)
        user = _get_user('admin')
        order = svc.create_order(patient, [t], FakeForm({'payment_amount': '0'}), user)
        order.status = OrderStatus.COMPLETED
        db.session.commit()

        ok, err = svc.send_back_order(order, '', user)
        assert ok is False
        assert 'reason' in err.lower()


def test_send_back_success(app):
    with app.app_context():
        patient = _make_patient()
        t = _make_test(code=f'SBOK{_u()}', name='SB2', price=5.0)
        user = _get_user('admin')
        order = svc.create_order(patient, [t], FakeForm({'payment_amount': '0'}), user)
        order.status = OrderStatus.COMPLETED
        db.session.commit()

        ok, err = svc.send_back_order(order, 'Value looks wrong', user)
        assert ok is True
        assert order.status == OrderStatus.CORRECTION
        assert order.correction_note == 'Value looks wrong'

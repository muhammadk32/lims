"""Tests for modules/lab/services.py — no HTTP."""
import uuid
import pytest

from extensions import db
from modules.orders.models import Order, OrderStatus
from modules.orders import services as osvc
from modules.lab import services as svc
from core.models import User


def _u():
    return uuid.uuid4().hex[:8].upper()


def _get_user(username):
    return User.query.filter_by(username=username).first()


def _make_test(**kw):
    from modules.tests.models import Test
    defaults = dict(code=f'LB{_u()}', name='LB', price=10.0,
                    unit='u', normal_range='1 - 10',
                    is_active=True, is_panel=False)
    defaults.update(kw)
    t = Test(**defaults)
    db.session.add(t)
    db.session.flush()
    return t


def _make_patient():
    from modules.patients.models import Patient
    p = Patient(patient_code=f'PLB{_u()}', full_name=f'Pat {_u()}')
    db.session.add(p)
    db.session.flush()
    return p


class FakeForm:
    def __init__(self, data=None):
        self.data = data or {}
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
        return []


def _make_verified_order():
    patient = _make_patient()
    t = _make_test(code=f'LBX{_u()}', name='Lab Test', price=10.0)
    user = _get_user('admin')
    order = osvc.create_order(patient, [t], FakeForm({'payment_amount': '0'}), user)

    item = order.top_level_items[0]
    item.result_value = '5'
    order.status = OrderStatus.COMPLETED
    db.session.commit()

    item.verified_at = __import__('datetime').datetime.utcnow()
    item.verified_by_id = user.id
    order.status = OrderStatus.APPROVED
    order.reported_at = __import__('datetime').datetime.utcnow()
    order.reported_by_id = user.id
    db.session.commit()

    return order, item, user


# ============================================================
# can_verify / labels
# ============================================================
def test_can_verify_roles(app):
    with app.app_context():
        admin = _get_user('admin')
        doctor = _get_user('doctor')
        tech = _get_user('tech')
        assert svc.can_verify(admin) is True
        assert svc.can_verify(doctor) is True
        assert svc.can_verify(tech) is False


def test_item_label_with_test(app):
    with app.app_context():
        patient = _make_patient()
        t = _make_test(code=f'LBL{_u()}', name='Label Test', price=5.0)
        user = _get_user('admin')
        order = osvc.create_order(patient, [t], FakeForm({'payment_amount': '0'}), user)
        item = order.top_level_items[0]
        assert svc.item_label(item) == 'Label Test'


def test_label_list_truncates(app):
    names = [f'Test{i}' for i in range(15)]
    s = svc.label_list(names, limit=5)
    assert 'Test0' in s
    assert 'Test4' in s
    assert '…and 10 more' in s


# ============================================================
# approve_items
# ============================================================
def test_approve_items_empty_returns_empty(app):
    with app.app_context():
        user = _get_user('admin')
        assert svc.approve_items([], user) == []


def test_approve_items_verifies_and_labels(app):
    with app.app_context():
        patient = _make_patient()
        t = _make_test(code=f'LBA{_u()}', name='ApproveMe', price=5.0)
        user = _get_user('admin')
        order = osvc.create_order(patient, [t], FakeForm({'payment_amount': '0'}), user)
        item = order.top_level_items[0]
        item.result_value = '5'
        order.status = OrderStatus.COMPLETED
        db.session.commit()

        labels = svc.approve_items([item], user)
        assert len(labels) == 1
        assert 'ApproveMe' in labels[0]
        assert item.verified_at is not None
        assert item.verified_by_id == user.id


def test_approve_items_promotes_order_to_approved(app):
    with app.app_context():
        patient = _make_patient()
        t = _make_test(code=f'LBA{_u()}', name='Appr2Test', price=5.0)
        user = _get_user('admin')
        order = osvc.create_order(patient, [t], FakeForm({'payment_amount': '0'}), user)
        item = order.top_level_items[0]
        item.result_value = '5'
        order.status = OrderStatus.COMPLETED
        db.session.commit()

        svc.approve_items([item], user)
        assert order.status == OrderStatus.APPROVED
        assert order.reported_at is not None


def test_approve_items_clears_correction_note(app):
    with app.app_context():
        order, item, user = _make_verified_order()
        item.correction_note = 'redo'
        item.verified_at = None
        db.session.commit()

        svc.approve_items([item], user)
        assert item.correction_note is None


# ============================================================
# send_back_items
# ============================================================
def test_send_back_sets_correction(app):
    with app.app_context():
        order, item, user = _make_verified_order()
        svc.send_back_items([item], 'redo please', user, order_note_mode='single')
        db.session.commit()
        assert item.correction_note == 'redo please'
        assert item.verified_at is None
        assert order.status == OrderStatus.CORRECTION
        assert order.correction_note is not None


def test_send_back_bulk_order_note_mode(app):
    with app.app_context():
        order, item, user = _make_verified_order()
        svc.send_back_items([item], 'bulk reason', user, order_note_mode='bulk')
        db.session.commit()
        assert order.correction_note == 'bulk reason'


def test_send_back_propagates_to_panel_children(app):
    with app.app_context():
        from modules.tests.models import Test, PanelParameter

        patient = _make_patient()
        panel = Test(code=f'LBP{_u()}', name='PanelSB', price=30.0,
                     is_panel=True, is_active=True)
        db.session.add(panel)
        db.session.flush()
        c1 = _make_test(code=f'LBC{_u()}', name='PChild1', price=0.0)
        c2 = _make_test(code=f'LBC{_u()}', name='PChild2', price=0.0)
        db.session.add(PanelParameter(panel_id=panel.id, test_id=c1.id, sort_order=0))
        db.session.add(PanelParameter(panel_id=panel.id, test_id=c2.id, sort_order=1))
        db.session.flush()

        user = _get_user('admin')
        order = osvc.create_order(patient, [panel], FakeForm({'payment_amount': '0'}), user)
        parent = order.top_level_items[0]
        for ch in parent.children:
            ch.result_value = '5'
        parent.verified_at = __import__('datetime').datetime.utcnow()
        order.status = OrderStatus.APPROVED
        db.session.commit()

        svc.send_back_items([parent], 'fix panel', user, order_note_mode='single')
        db.session.commit()

        for ch in parent.children:
            assert ch.correction_note == 'fix panel'

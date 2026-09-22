"""Tests for modules/results/services.py — no HTTP."""
import uuid
import pytest

from extensions import db
from modules.orders.models import Order, OrderStatus
from modules.orders import services as osvc
from modules.results import services as svc
from core.models import User


def _u():
    return uuid.uuid4().hex[:8].upper()


def _get_user(username):
    return User.query.filter_by(username=username).first()


def _make_test(**kw):
    from modules.tests.models import Test
    defaults = dict(code=f'RS{_u()}', name='RS', price=10.0,
                    unit='u', normal_range='1 - 10',
                    is_active=True, is_panel=False)
    defaults.update(kw)
    t = Test(**defaults)
    db.session.add(t)
    db.session.flush()
    return t


def _make_patient():
    from modules.patients.models import Patient
    p = Patient(patient_code=f'PRX{_u()}', full_name=f'Pat {_u()}')
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


def _make_order():
    patient = _make_patient()
    t = _make_test(code=f'RX{_u()}', name='RX Test', price=10.0)
    user = _get_user('admin')
    order = osvc.create_order(patient, [t], FakeForm({'payment_amount': '0'}), user)
    return order, user


# ============================================================
# save_order_results
# ============================================================
def test_save_results_fills_values(app):
    with app.app_context():
        order, user = _make_order()
        item = order.top_level_items[0]
        form = FakeForm({f'result_value_{item.id}': '7',
                         f'result_notes_{item.id}': 'normal'})
        mode, o = svc.save_order_results(order, form, user)
        assert mode == 'saved'
        assert item.result_value == '7'
        assert item.result_notes == 'normal'


def test_save_results_auto_completes_when_all_done(app):
    with app.app_context():
        order, user = _make_order()
        item = order.top_level_items[0]
        form = FakeForm({f'result_value_{item.id}': '7'})
        svc.save_order_results(order, form, user)
        assert order.status == OrderStatus.COMPLETED


def test_save_results_clears_correction_flag(app):
    with app.app_context():
        order, user = _make_order()
        item = order.top_level_items[0]
        item.correction_note = 'redo'
        item.result_value = '5'
        db.session.commit()

        form = FakeForm({f'result_value_{item.id}': '6'})
        svc.save_order_results(order, form, user)
        assert item.correction_note is None


def test_save_results_resets_approved_order(app):
    with app.app_context():
        order, user = _make_order()
        item = order.top_level_items[0]
        item.result_value = '5'
        item.verified_at = __import__('datetime').datetime.utcnow()
        order.status = OrderStatus.APPROVED
        order.reported_at = __import__('datetime').datetime.utcnow()
        db.session.commit()

        form = FakeForm({f'result_value_{item.id}': '9'})
        mode, _ = svc.save_order_results(order, form, user)
        assert mode == 'reset'
        assert order.status == OrderStatus.COMPLETED
        assert order.reported_at is None
        assert item.verified_at is None


def test_save_results_no_change_on_approved(app):
    with app.app_context():
        order, user = _make_order()
        item = order.top_level_items[0]
        item.result_value = '5'
        order.status = OrderStatus.APPROVED
        db.session.commit()

        form = FakeForm({f'result_value_{item.id}': '5'})
        mode, _ = svc.save_order_results(order, form, user)
        assert mode == 'saved'
        assert order.status in (OrderStatus.APPROVED, OrderStatus.COMPLETED)


def test_save_results_resolves_correction_state(app):
    with app.app_context():
        order, user = _make_order()
        item = order.top_level_items[0]
        item.correction_note = 'fix'
        item.result_value = '5'
        order.status = OrderStatus.CORRECTION
        order.correction_note = 'fix'
        db.session.commit()

        form = FakeForm({f'result_value_{item.id}': '7'})
        mode, _ = svc.save_order_results(order, form, user)
        assert mode == 'saved'
        assert order.correction_note is None


# ============================================================
# clear_result_value
# ============================================================
def test_clear_result_success(app):
    with app.app_context():
        order, user = _make_order()
        item = order.top_level_items[0]
        item.result_value = '5'
        db.session.commit()

        o, was_approved = svc.clear_result_value(item, user)
        assert o.id == order.id
        assert item.result_value is None
        assert was_approved is False


def test_clear_result_resets_approved(app):
    with app.app_context():
        order, user = _make_order()
        item = order.top_level_items[0]
        item.result_value = '5'
        order.status = OrderStatus.APPROVED
        db.session.commit()

        o, was_approved = svc.clear_result_value(item, user)
        assert was_approved is True
        assert order.status == OrderStatus.COMPLETED
        assert order.reported_at is None


def test_clear_result_cancelled_raises(app):
    with app.app_context():
        order, user = _make_order()
        order.status = OrderStatus.CANCELLED
        db.session.commit()
        item = order.top_level_items[0]
        with pytest.raises(ValueError, match='cancelled'):
            svc.clear_result_value(item, user)


# ============================================================
# get_patient_orders
# ============================================================
def test_get_patient_orders_newest_first(app):
    with app.app_context():
        order, _user = _make_order()
        orders = svc.get_patient_orders(order.patient_id)
        assert len(orders) >= 1
        assert orders[0].id == order.id


def test_get_patient_orders_excludes_cancelled(app):
    with app.app_context():
        order, user = _make_order()
        order.status = OrderStatus.CANCELLED
        db.session.commit()
        orders = svc.get_patient_orders(order.patient_id)
        assert all(o.status != OrderStatus.CANCELLED for o in orders)

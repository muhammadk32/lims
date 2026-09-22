"""Tests for modules/test_settings/services.py — no HTTP."""
import uuid
import pytest

from extensions import db
from modules.tests.models import Test, TestCategory, PanelParameter
from modules.test_settings import services as svc


def _u():
    return uuid.uuid4().hex[:8].upper()


# ============================================================
# Categories
# ============================================================
def test_create_category_success(app):
    with app.app_context():
        name = f'Chemistry {_u()}'
        ok, err, cat = svc.create_category(name, 'Chem tests')
        assert ok is True
        assert cat.id
        assert cat.name == name


def test_create_category_empty_name(app):
    with app.app_context():
        ok, err, cat = svc.create_category('', '')
        assert ok is False
        assert 'required' in err.lower()
        assert cat is None


def test_create_category_too_long(app):
    with app.app_context():
        ok, err, cat = svc.create_category('x' * 100, '')
        assert ok is False
        assert 'too long' in err.lower()


def test_create_category_duplicate(app):
    with app.app_context():
        name = f'Biochem {_u()}'
        svc.create_category(name, '')
        ok, err, cat = svc.create_category(name, '')
        assert ok is False
        assert 'already exists' in err.lower()


def test_create_category_case_insensitive_dup(app):
    with app.app_context():
        base = f'Case {_u()}'
        svc.create_category(base, '')
        ok, err, cat = svc.create_category(base.upper(), '')
        assert ok is False
        assert 'already exists' in err.lower()


def test_update_category_success(app):
    with app.app_context():
        _ok, _e, cat = svc.create_category(f'Old {_u()}', 'desc')
        ok, err = svc.update_category(cat, f'New {_u()}', 'new desc')
        assert ok is True


def test_update_category_empty_name(app):
    with app.app_context():
        _ok, _e, cat = svc.create_category(f'Old {_u()}', '')
        ok, err = svc.update_category(cat, '', '')
        assert ok is False


def test_update_category_dup_other(app):
    with app.app_context():
        name_a = f'CatA {_u()}'
        svc.create_category(name_a, '')
        _ok, _e, catB = svc.create_category(f'CatB {_u()}', '')
        ok, err = svc.update_category(catB, name_a, '')
        assert ok is False
        assert 'already exists' in err.lower()


def test_update_category_same_name_ok(app):
    with app.app_context():
        name = f'Self {_u()}'
        _ok, _e, cat = svc.create_category(name, '')
        ok, err = svc.update_category(cat, name, 'updated')
        assert ok is True


def test_delete_category_success(app):
    with app.app_context():
        name = f'Empty {_u()}'
        _ok, _e, cat = svc.create_category(name, '')
        ok, err, count = svc.delete_category(cat)
        assert ok is True
        assert TestCategory.query.filter_by(name=name).first() is None


def test_delete_category_with_tests_fails(app):
    with app.app_context():
        _ok, _e, cat = svc.create_category(f'Used {_u()}', '')
        t = Test(code=f'DELCHK{_u()}', name='DC', category_id=cat.id,
                 price=1.0, is_active=True)
        db.session.add(t)
        db.session.commit()

        ok, err, count = svc.delete_category(cat)
        assert ok is False
        assert count > 0


# ============================================================
# Panels
# ============================================================
class FakeForm:
    def __init__(self, data=None, lists=None):
        self.data = data or {}
        self.lists = lists or {}
    def get(self, key, default=None):
        return self.data.get(key, default)
    def getlist(self, key, type=None):
        return self.lists.get(key, [])


def test_create_panel_success(app):
    with app.app_context():
        c1 = Test(code=f'PNLC{_u()}', name='C1', price=0.0, is_active=True)
        c2 = Test(code=f'PNLC{_u()}', name='C2', price=0.0, is_active=True)
        db.session.add_all([c1, c2])
        db.session.flush()

        code = f'PNLNEW{_u()}'
        form = FakeForm(
            data={'code': code, 'name': 'New Panel', 'price': '50'},
            lists={'parameter_ids': [str(c1.id), str(c2.id)]},
        )
        ok, errors, panel = svc.create_panel(form)
        assert ok is True, errors
        assert panel.id
        assert panel.is_panel is True
        assert panel.price == 50.0

        params = PanelParameter.query.filter_by(panel_id=panel.id).all()
        assert len(params) == 2


def test_create_panel_missing_code(app):
    with app.app_context():
        form = FakeForm(data={'name': 'No Code', 'price': '10'})
        ok, errors, panel = svc.create_panel(form)
        assert ok is False
        assert any('Code' in e for e in errors)


def test_create_panel_duplicate_code(app):
    with app.app_context():
        existing_code = f'DUPPNL{_u()}'
        t = Test(code=existing_code, name='Existing', is_active=True, price=0.0)
        db.session.add(t)
        db.session.commit()

        form = FakeForm(data={'code': existing_code, 'name': 'Dup', 'price': '10'})
        ok, errors, panel = svc.create_panel(form)
        assert ok is False
        assert any('exists' in e.lower() for e in errors)


def test_create_panel_negative_price(app):
    with app.app_context():
        form = FakeForm(data={'code': f'NEGP{_u()}', 'name': 'Neg', 'price': '-5'})
        ok, errors, panel = svc.create_panel(form)
        assert ok is False
        assert any('0' in e for e in errors)


def test_update_panel_success(app):
    with app.app_context():
        c1 = Test(code=f'UPC{_u()}', name='UPC1', price=0.0, is_active=True)
        db.session.add(c1)
        db.session.flush()

        code = f'UPPNL{_u()}'
        form = FakeForm(
            data={'code': code, 'name': 'UP Panel', 'price': '25'},
            lists={'parameter_ids': [str(c1.id)]},
        )
        _ok, _e, panel = svc.create_panel(form)
        assert panel is not None

        new_form = FakeForm(
            data={'code': code, 'name': 'Renamed', 'price': '30', 'is_active': '1'},
            lists={'parameter_ids': []},
        )
        ok, errors = svc.update_panel(panel, new_form)
        assert ok is True, errors
        assert panel.name == 'Renamed'
        assert panel.price == 30.0


def test_delete_panel_success(app):
    with app.app_context():
        form = FakeForm(data={'code': f'DELPNL{_u()}', 'name': 'Del', 'price': '10'})
        _ok, _e, panel = svc.create_panel(form)
        ok, err = svc.delete_panel(panel)
        assert ok is True


def test_delete_panel_used_in_order_fails(app):
    with app.app_context():
        from modules.patients.models import Patient
        from modules.orders import services as osvc
        from core.models import User

        c1 = Test(code=f'DUPC{_u()}', name='DUPC1', price=0.0, is_active=True)
        db.session.add(c1)
        db.session.flush()
        form = FakeForm(
            data={'code': f'USEDPNL{_u()}', 'name': 'Used', 'price': '10'},
            lists={'parameter_ids': [str(c1.id)]},
        )
        _ok, _e, panel = svc.create_panel(form)

        patient = Patient(patient_code=f'PNLP{_u()}', full_name='PanelPatient')
        db.session.add(patient)
        db.session.flush()
        admin = User.query.filter_by(username='admin').first()

        class SimpleForm:
            data = {'payment_amount': '0'}
            def get(self, k, d=None, type=None): return self.data.get(k, d)
            def getlist(self, k, type=None): return []

        osvc.create_order(patient, [panel], SimpleForm(), admin)

        ok, err = svc.delete_panel(panel)
        assert ok is False
        assert 'order' in err.lower()


# ============================================================
# update_test_format
# ============================================================
def test_update_test_format_valid(app):
    with app.app_context():
        t = Test(code=f'FMT{_u()}', name='FMT', is_active=True, price=0.0)
        db.session.add(t)
        db.session.commit()

        result = svc.update_test_format(t, 'numeric')
        assert result is not None
        assert result['ok'] is True
        assert t.result_format == 'numeric'


def test_update_test_format_invalid_returns_none(app):
    with app.app_context():
        t = Test(code=f'FMTB{_u()}', name='FMTB', is_active=True, price=0.0)
        db.session.add(t)
        db.session.commit()
        result = svc.update_test_format(t, 'nonsense_format')
        assert result is None


def test_update_test_format_to_panel(app):
    with app.app_context():
        t = Test(code=f'F2P{_u()}', name='F2P', is_active=True, price=5.0,
                 unit='mg', normal_range='1-5')
        db.session.add(t)
        db.session.commit()

        result = svc.update_test_format(t, 'panel')
        assert result['is_panel'] is True
        assert t.is_panel is True
        assert t.unit is None
        assert t.normal_range is None

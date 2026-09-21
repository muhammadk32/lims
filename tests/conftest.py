"""
Shared pytest fixtures.
"""
import os
import sys
import pytest

# Ensure project root is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from extensions import db as _db
from core.models import User
from core.roles import Role
from modules.patients.models import Patient
from modules.tests.models import Test, TestCategory


@pytest.fixture(scope='session')
def app():
    """Create the app once per test session.

    IMPORTANT: we do NOT keep an app_context open for the whole session —
    doing so caches `g._login_user` across tests and lets Flask-Login
    return stale authenticated users in unrelated tests.
    """
    app = create_app('testing')

    # Setup: create tables + seed data (in a short-lived app context)
    with app.app_context():
        _db.create_all()
        _seed_test_data()

    yield app

    # Teardown
    with app.app_context():
        _db.session.remove()
        _db.drop_all()


def _seed_test_data():
    """Minimal seed for tests."""
    admin = User(username='admin', full_name='Test Admin', role=Role.ADMIN)
    admin.set_password('admin123')
    _db.session.add(admin)

    doctor = User(username='doctor', full_name='Test Doctor', role=Role.DOCTOR)
    doctor.set_password('doc123')
    _db.session.add(doctor)

    tech = User(username='tech', full_name='Test Tech', role=Role.TECHNICIAN)
    tech.set_password('tech123')
    _db.session.add(tech)

    recep = User(username='recep.lisa', full_name='Test Receptionist', role=Role.RECEPTIONIST)
    recep.set_password('recep123')
    _db.session.add(recep)

    cat = TestCategory(name='Hematology')
    _db.session.add(cat)
    _db.session.flush()

    t = Test(code='CBC', name='Complete Blood Count', category_id=cat.id,
             price=15.0, unit='cells/µL', normal_range='See report')
    _db.session.add(t)

    t2 = Test(code='FBS', name='Fasting Blood Sugar', category_id=cat.id,
              price=5.0, unit='mg/dL', normal_range='70 - 100')
    _db.session.add(t2)

    p = Patient(patient_code='P001', full_name='John Test', gender='Male', age=30)
    _db.session.add(p)

    _db.session.commit()


@pytest.fixture
def client(app):
    """A fresh test client per test."""
    return app.test_client()


@pytest.fixture
def db(app):
    return _db


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture(autouse=True)
def _clean_session(app):
    """Roll back uncommitted changes + clear Flask-Login cache after each test."""
    yield
    with app.app_context():
        _db.session.rollback()
        # Clear Flask-Login's cached user for this app context
        from flask import g
        if hasattr(g, '_login_user'):
            delattr(g, '_login_user')


def login(client, username, password):
    return client.post('/login', data={
        'username': username,
        'password': password,
    }, follow_redirects=True)


def logout(client):
    return client.get('/logout', follow_redirects=True)
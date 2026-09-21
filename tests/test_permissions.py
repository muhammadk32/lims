from tests.conftest import login
from core.roles import Role, has_permission


def test_permission_matrix():
    assert has_permission(Role.ADMIN, 'manage_users')
    assert not has_permission(Role.DOCTOR, 'manage_users')
    assert has_permission(Role.TECHNICIAN, 'enter_results')
    assert not has_permission(Role.DOCTOR, 'enter_results')
    assert has_permission(Role.RECEPTIONIST, 'record_payment')
    assert not has_permission(Role.TECHNICIAN, 'record_payment')
    assert not has_permission(Role.DOCTOR, 'manage_tests')


def test_admin_can_access_users(client):
    login(client, 'admin', 'admin123')
    r = client.get('/users/')
    assert r.status_code == 200


def test_doctor_cannot_access_users(client):
    login(client, 'doctor', 'doc123')
    r = client.get('/users/', follow_redirects=False)
    assert r.status_code == 403


def test_admin_can_access_audit(client):
    login(client, 'admin', 'admin123')
    r = client.get('/audit/')
    assert r.status_code == 200


def test_doctor_cannot_access_audit(client):
    login(client, 'doctor', 'doc123')
    r = client.get('/audit/', follow_redirects=False)
    assert r.status_code == 403


def test_403_page_renders(client):
    login(client, 'doctor', 'doc123')
    r = client.get('/users/', follow_redirects=False)
    assert r.status_code == 403
    assert b'Access Denied' in r.data or b'403' in r.data
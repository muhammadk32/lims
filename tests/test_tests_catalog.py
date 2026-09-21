from tests.conftest import login
from modules.tests.models import Test


def test_list_tests(client):
    login(client, 'admin', 'admin123')
    r = client.get('/tests/')
    assert r.status_code == 200
    assert b'CBC' in r.data


def test_create_test_as_admin(client, app):
    login(client, 'admin', 'admin123')
    r = client.post('/tests/new', data={
        'code': 'NEW1',
        'name': 'New Test',
        'category_id': '',
        'price': '12.5',
        'unit': 'mg',
        'normal_range': '5 - 10',
    }, follow_redirects=True)
    assert r.status_code == 200

    with app.app_context():
        t = Test.query.filter_by(code='NEW1').first()
        assert t is not None
        assert t.price == 12.5


def test_duplicate_test_code_rejected(client):
    login(client, 'admin', 'admin123')
    r = client.post('/tests/new', data={
        'code': 'CBC',
        'name': 'Dupe CBC',
        'price': '5',
    }, follow_redirects=True)
    assert b'already exists' in r.data.lower()


def test_technician_cannot_create_test(client):
    login(client, 'tech', 'tech123')
    r = client.get('/tests/new', follow_redirects=False)
    assert r.status_code == 403
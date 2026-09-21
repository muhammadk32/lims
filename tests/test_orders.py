from tests.conftest import login
from modules.orders.models import Order
from modules.patients.models import Patient
from modules.tests.models import Test


def test_new_order_page_loads(client):
    login(client, 'admin', 'admin123')
    r = client.get('/orders/new')
    assert r.status_code == 200
    assert b'New Order' in r.data


def test_create_order(client, app):
    login(client, 'admin', 'admin123')

    with app.app_context():
        p = Patient.query.first()
        pid = p.id
        tests = Test.query.all()
        tids = [str(t.id) for t in tests]

    before = None
    with app.app_context():
        before = Order.query.count()

    r = client.post('/orders/new', data={
        'patient_id': str(pid),
        'test_ids': tids,
    }, follow_redirects=True)
    assert r.status_code == 200

    with app.app_context():
        after = Order.query.count()
        assert after == before + 1
        o = Order.query.order_by(Order.id.desc()).first()
        assert o.patient_id == pid
        assert o.item_count == len(tids)
        assert o.total_amount > 0


def test_doctor_can_create_order(client):
    login(client, 'doctor', 'doc123')
    r = client.get('/orders/new')
    assert r.status_code == 200


def test_receptionist_cannot_enter_results(client, app):
    """Receptionist does NOT have 'enter_results' permission → 403."""
    # Admin creates an order
    login(client, 'admin', 'admin123')

    with app.app_context():
        p = Patient.query.first()
        t = Test.query.first()
        pid, tid = p.id, t.id

    client.post('/orders/new', data={'patient_id': str(pid), 'test_ids': [str(tid)]})

    with app.app_context():
        o = Order.query.order_by(Order.id.desc()).first()
        oid = o.id

    # Log out, then log in as receptionist
    client.get('/logout')
    login(client, 'recep.lisa', 'recep123')

    # Receptionist should be denied access to result entry
    r = client.get(f'/results/enter/{oid}', follow_redirects=False)
    assert r.status_code == 403
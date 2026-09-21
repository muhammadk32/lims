import uuid
from tests.conftest import login
from modules.patients.models import Patient
from modules.tests.models import Test
from modules.orders.models import Order, OrderItem
from modules.billing.models import Payment


def _make_order(app):
    """Create a throwaway order with a unique code for the test."""
    with app.app_context():
        from extensions import db
        p = Patient.query.first()
        t = Test.query.first()
        o = Order(
            order_code=f'TEST-{uuid.uuid4().hex[:8]}',
            patient_id=p.id,
            total_amount=t.price,
        )
        db.session.add(o)
        db.session.flush()
        db.session.add(OrderItem(order_id=o.id, test_id=t.id, price=t.price))
        db.session.commit()
        return o.id


def test_billing_page_loads(client):
    login(client, 'admin', 'admin123')
    r = client.get('/billing/')
    assert r.status_code == 200


def test_record_payment(client, app):
    oid = _make_order(app)
    login(client, 'admin', 'admin123')

    before = None
    with app.app_context():
        before = Payment.query.count()

    r = client.post(f'/billing/order/{oid}/pay', data={
        'amount': '5.00',
        'method': 'cash',
    }, follow_redirects=True)
    assert r.status_code == 200

    with app.app_context():
        after = Payment.query.count()
        assert after == before + 1
        p = Payment.query.order_by(Payment.id.desc()).first()
        assert p.amount == 5.0
        assert p.method == 'cash'


def test_overpayment_rejected(client, app):
    oid = _make_order(app)
    login(client, 'admin', 'admin123')
    r = client.post(f'/billing/order/{oid}/pay', data={
        'amount': '99999',
        'method': 'cash',
    }, follow_redirects=True)
    assert b'exceeds' in r.data.lower() or b'balance due' in r.data.lower()


def test_technician_cannot_access_billing(client):
    login(client, 'tech', 'tech123')
    r = client.get('/billing/', follow_redirects=False)
    assert r.status_code == 403
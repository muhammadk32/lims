"""
Populate the database with realistic sample data.

Usage:
    python -m scripts.seed_data
    python -m scripts.seed_data --patients 100 --orders 500
    python -m scripts.seed_data --wipe   # wipe existing demo data first

Safe: only adds data. Does NOT touch existing records unless --wipe is passed.
"""
import argparse
import random
from datetime import datetime, timedelta

from app import create_app
from extensions import db
from core.models import User
from core.roles import Role
from modules.patients.models import Patient
from modules.tests.models import Test
from modules.orders.models import Order, OrderItem, OrderStatus
from modules.billing.models import Payment, PaymentMethod


FIRST_NAMES = [
    'James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda',
    'William', 'Elizabeth', 'David', 'Barbara', 'Richard', 'Susan', 'Joseph',
    'Jessica', 'Thomas', 'Sarah', 'Charles', 'Karen', 'Aisha', 'Fatima', 'Omar',
    'Zainab', 'Ahmed', 'Sana', 'Bilal', 'Hira', 'Usman', 'Maryam',
]
LAST_NAMES = [
    'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller',
    'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez',
    'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin',
    'Khan', 'Ahmed', 'Iqbal', 'Malik', 'Hussain', 'Raza', 'Sheikh',
]
GENDERS = ['Male', 'Female']
BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']


def _random_name():
    return f'{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}'


def _random_phone():
    return f'+1 555 {random.randint(1000, 9999)}'


def _random_email(name):
    user = name.lower().replace(' ', '.')
    return f'{user}{random.randint(1, 999)}@example.com'


def _random_dob():
    """Random birthdate 1950-2005."""
    year = random.randint(1950, 2005)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return datetime(year, month, day).date()


def _random_result(normal_range):
    """Generate a plausible result - mostly normal, sometimes abnormal."""
    import re
    if not normal_range:
        return str(random.randint(1, 100))

    m = re.match(r'^\s*(-?\d+(?:\.\d+)?)\s*[-\u2013]\s*(-?\d+(?:\.\d+)?)\s*$', normal_range)
    if m:
        low, high = float(m.group(1)), float(m.group(2))
        if random.random() < 0.75:
            return f'{random.uniform(low, high):.1f}'
        else:
            if random.random() < 0.5:
                return f'{high * random.uniform(1.05, 1.5):.1f}'
            else:
                return f'{low * random.uniform(0.5, 0.95):.1f}'

    m = re.match(r'^\s*[<\u2264]\s*(-?\d+(?:\.\d+)?)\s*$', normal_range)
    if m:
        bound = float(m.group(1))
        return f'{random.uniform(0, bound * 0.9):.1f}' if random.random() < 0.75 else f'{bound * 1.2:.1f}'

    m = re.match(r'^\s*[>\u2265]\s*(-?\d+(?:\.\d+)?)\s*$', normal_range)
    if m:
        bound = float(m.group(1))
        return f'{bound * 1.1:.1f}' if random.random() < 0.75 else f'{bound * 0.7:.1f}'

    if normal_range.lower() in ('negative', 'no growth', 'normal'):
        return 'Negative' if random.random() < 0.8 else 'Positive'

    return 'Normal'


def _unique_order_code(dt):
    """Generate a unique order code — retries on collision."""
    for _ in range(20):
        code = f'O{dt.strftime("%y%m%d%H%M%S")}{random.randint(1000, 9999)}'
        if not Order.query.filter_by(order_code=code).first():
            return code
    # Fallback with UUID if we somehow can't find one
    import uuid
    return f'O{dt.strftime("%y%m%d%H%M%S")}{uuid.uuid4().hex[:4]}'


def seed(patients=50, orders=200, wipe=False):
    app = create_app()
    with app.app_context():
        if wipe:
            print('⚠️  Wiping existing demo data...')
            Payment.query.delete()
            OrderItem.query.delete()
            Order.query.delete()
            Patient.query.delete()
            db.session.commit()

        # Ensure tests exist
        tests = Test.query.filter_by(is_active=True).all()
        if not tests:
            print('❌ No tests found. Run app once to seed the catalog first.')
            return

        # Ensure at least one doctor exists
        doctor = User.query.filter_by(role=Role.DOCTOR).first()
        if not doctor:
            doctor = User(username='dr.demo', full_name='Dr. Demo', role=Role.DOCTOR)
            doctor.set_password('demo123')
            db.session.add(doctor)
            db.session.commit()
            print('👨‍⚕️  Created demo doctor (dr.demo / demo123)')

        print(f'📝 Creating {patients} patients...')
        patient_objs = []
        for i in range(patients):
            name = _random_name()
            code = f'P{datetime.now().strftime("%y%m%d")}{random.randint(10000, 99999)}'
            while Patient.query.filter_by(patient_code=code).first():
                code = f'P{datetime.now().strftime("%y%m%d")}{random.randint(10000, 99999)}'

            p = Patient(
                patient_code=code,
                full_name=name,
                age=random.randint(1, 85),
                date_of_birth=_random_dob(),
                gender=random.choice(GENDERS),
                phone=_random_phone(),
                email=_random_email(name),
                address=f'{random.randint(1, 999)} Main St, Springfield',
                blood_group=random.choice(BLOOD_GROUPS),
            )
            db.session.add(p)
            patient_objs.append(p)

        db.session.commit()
        print(f'✅ Created {len(patient_objs)} patients.')

        print(f'🧾 Creating {orders} orders with results and payments...')
        order_count = 0
        payment_count = 0

        for _ in range(orders):
            p = random.choice(patient_objs)
            chosen_tests = random.sample(tests, k=random.randint(1, min(5, len(tests))))
            total = sum(t.price for t in chosen_tests)

            days_ago = random.randint(0, 60)
            order_date = datetime.utcnow() - timedelta(
                days=days_ago, hours=random.randint(0, 23)
            )

            order = Order(
                order_code=_unique_order_code(order_date),
                patient_id=p.id,
                doctor_id=doctor.id,
                total_amount=total,
                created_at=order_date,
                updated_at=order_date,
            )
            db.session.add(order)
            db.session.flush()

            all_results_done = True
            for t in chosen_tests:
                item = OrderItem(
                    order_id=order.id,
                    test_id=t.id,
                    price=t.price,
                )
                if random.random() < 0.7:
                    item.result_value = _random_result(t.normal_range)
                    item.status = 'completed'
                else:
                    item.status = 'pending'
                    all_results_done = False
                db.session.add(item)

            # Order status
            if all_results_done and random.random() < 0.9:
                order.status = OrderStatus.COMPLETED
            elif random.random() < 0.5:
                order.status = OrderStatus.COLLECTED
                order.sample_collected_at = order_date + timedelta(hours=random.randint(1, 6))
            else:
                order.status = OrderStatus.PENDING

            # Payment: 60% pay in full, 25% partial, 15% unpaid
            r = random.random()
            if r < 0.60:
                amount = total
            elif r < 0.85:
                amount = round(total * random.uniform(0.3, 0.8), 2)
            else:
                amount = 0

            if amount > 0:
                payment = Payment(
                    order_id=order.id,
                    amount=amount,
                    method=random.choice(PaymentMethod.CHOICES),
                    reference=f'TXN{random.randint(100000, 999999)}',
                    received_by_id=doctor.id,
                    created_at=order_date,
                    updated_at=order_date,
                )
                db.session.add(payment)
                payment_count += 1

            order_count += 1
            if order_count % 50 == 0:
                db.session.commit()
                print(f'   ... {order_count} orders')

        db.session.commit()

        # Sync order paid flags
        print('🔁 Syncing paid flags...')
        for o in Order.query.all():
            o.paid = o.is_fully_paid
        db.session.commit()

        print()
        print('✅ Seed complete!')
        print(f'   Patients: {Patient.query.count()}')
        print(f'   Orders:   {Order.query.count()}')
        print(f'   Payments: {Payment.query.count()}')
        print(f'   Tests:    {Test.query.count()}')
        print()
        print('Login: admin / admin123')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Seed sample data into LabMS.')
    parser.add_argument('--patients', type=int, default=50,
                        help='Number of patients to create (default 50)')
    parser.add_argument('--orders', type=int, default=200,
                        help='Number of orders to create (default 200)')
    parser.add_argument('--wipe', action='store_true',
                        help='Delete existing patients/orders/payments first')
    args = parser.parse_args()

    seed(patients=args.patients, orders=args.orders, wipe=args.wipe)
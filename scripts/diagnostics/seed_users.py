from app import create_app
from extensions import db
from core.models import User
from core.roles import Role

app = create_app()

with app.app_context():
    demo = [
        ('dr.smith',   'Dr. John Smith',  'smith@lab.local', Role.DOCTOR,       'doctor123'),
        ('tech.anna',  'Anna Technician', 'anna@lab.local',  Role.TECHNICIAN,   'tech1234'),
        ('recep.lisa', 'Lisa Reception',  'lisa@lab.local',  Role.RECEPTIONIST, 'recep123'),
    ]

    for username, name, email, role, pw in demo:
        if not User.query.filter_by(username=username).first():
            u = User(username=username, full_name=name, email=email, role=role)
            u.set_password(pw)
            db.session.add(u)
            print('Created', username, '→', role)
        else:
            print('Exists ', username)

    db.session.commit()

    print()
    print('Accounts ready:')
    print('  admin      / admin123   (Administrator)')
    print('  dr.smith   / doctor123  (Doctor)')
    print('  tech.anna  / tech1234   (Lab Technician)')
    print('  recep.lisa / recep123   (Receptionist)')
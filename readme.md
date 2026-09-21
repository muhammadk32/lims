# 🔬 LabMS — Laboratory Management System

A complete lab management system built with **Flask**, **SQLAlchemy**, and **Bootstrap 5**.

## Features

- 🔐 **Authentication & Roles** — admin, doctor, technician, receptionist
- 🧑 **Patient Management** — register, search, edit, archive
- 🧪 **Lab Test Catalog** — 34 pre-seeded common tests, categories, pricing
- 📝 **Orders** — multi-test orders with auto-total, status workflow
- 📋 **Results** — bulk entry, auto-abnormal detection, auto-complete
- 📄 **PDF Reports** — professional lab reports with abnormal highlighting
- 💵 **Billing** — invoices, partial payments, payment methods, revenue reports
- 📊 **Dashboard** — charts, KPIs, top tests, top patients, pending work
- 🛡️ **Audit Log** — every action tracked with user, IP, timestamp
- 🎨 **Polished UI** — sidebar, dark mode, toasts, breadcrumbs, mobile responsive

## Quick Start

### 1. Clone & set up

```bash
git clone <your-repo-url> labms
cd labms
python -m venv venv
source venv/bin/activate         # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env — at minimum, change SECRET_KEY
```

### 3. Initialize database

```bash
flask db upgrade
python app.py
```

First run creates `database.db` and seeds:
- Admin user: `admin / admin123`
- 34 common lab tests

### 4. Log in

Open http://localhost:5000 → log in with `admin / admin123`.

## Development

```bash
make run          # Start dev server
make test         # Run tests
make seed         # Populate with sample data (50 patients, 200 orders)
make backup       # Create a DB backup
make migrate      # Apply DB migrations
make logs         # Tail app.log
```

## Project Structure

```
lab_management_system/
├── app.py                  # App factory
├── config.py               # Configuration classes
├── extensions.py           # Flask extensions
├── requirements.txt
├── pytest.ini
├── Makefile
├── .env.example
├── core/                   # Shared: models, roles, decorators, audit, logging
├── modules/                # Feature modules (one per menu item)
│   ├── auth/
│   ├── dashboard/
│   ├── patients/
│   ├── tests/
│   ├── orders/
│   ├── results/
│   ├── reports/
│   ├── billing/
│   ├── users/
│   └── audit/
├── templates/              # Global templates + layout
├── static/                 # CSS + JS
├── migrations/             # Alembic migrations
├── scripts/                # seed_data, backup, restore
├── tests/                  # pytest suite
└── logs/                   # app.log, errors.log
```

## Roles & Permissions

| Action | Admin | Doctor | Technician | Receptionist |
|--------|:-----:|:------:|:----------:|:------------:|
| Manage users | ✅ | | | |
| Manage test catalog | ✅ | | | |
| Register patients | ✅ | | | ✅ |
| Create orders | ✅ | ✅ | | ✅ |
| Enter results | ✅ | | ✅ | |
| Record payments | ✅ | | | ✅ |
| View billing | ✅ | | | ✅ |
| View reports | ✅ | ✅ | ✅ | ✅ |
| View audit log | ✅ | | | |

## Production Deployment

### Switch to PostgreSQL

1. Create a dedicated DB and user:

```bash
sudo -u postgres psql
```

```sql
CREATE USER lms_user WITH PASSWORD 'strong_password';
CREATE DATABASE lab_management_db OWNER lms_user;
GRANT ALL PRIVILEGES ON DATABASE lab_management_db TO lms_user;
\q
```

2. Update `.env`:

```
DATABASE_URL=postgresql://lms_user:strong_password@localhost:5432/lab_management_db
SECRET_KEY=<64-char random>
FLASK_ENV=production
```

3. Install Postgres driver and migrate:

```bash
pip install psycopg2-binary
flask db upgrade
```

### Run with Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

### Nginx reverse proxy (example)

```nginx
server {
    listen 80;
    server_name lab.example.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /path/to/labms/static/;
    }
}
```

### Backups (cron)

```cron
0 2 * * * cd /path/to/labms && /path/to/venv/bin/python -m scripts.backup >> logs/backup.log 2>&1
```

## Testing

```bash
pytest -v
```

40+ tests covering auth, CRUD, permissions, validators, billing.

## Health Check

```
GET /healthz
→ {"status": "ok", "db": "ok", "version": "1.0.0"}
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `No such table` | Run `flask db upgrade` |
| Can't log in | Reset admin: `python -c "from app import create_app; from extensions import db; from core.models import User; app=create_app(); ctx=app.app_context(); ctx.push(); u=User.query.filter_by(username='admin').first(); u.set_password('newpass'); db.session.commit()"` |
| Port 5000 in use | Change `port=5000` in `app.py` |
| PDF missing rows | Check `reportlab` installed: `pip install reportlab` |

## License

MIT — free to use, modify, and deploy.
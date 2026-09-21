"""Application entry point.

Factory + wiring only. Everything else lives in `core/`.
"""
import os
from flask import Flask

from config import config_map
from extensions import db, login_manager, migrate
from core.logging_config import setup_logging
from core.branding import inject_branding
from core.context import register_context_processors
from core.filters import register_filters
from core.errors import register_error_handlers
from core.blueprints import register_blueprints
from core.cli import register_cli


def create_app(config_name=None):
    """Application factory."""
    config_name = config_name or os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_map[config_name])

    # ---------- Logging ----------
    setup_logging(app)

    # ---------- Extensions ----------
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # ---------- Branding upload folder ----------
    upload_dir = os.path.join(app.root_path, 'static', 'uploads', 'branding')
    os.makedirs(upload_dir, exist_ok=True)

    # ---------- Wiring ----------
    inject_branding(app)
    register_filters(app)
    register_context_processors(app)
    register_blueprints(app)
    register_error_handlers(app)
    register_cli(app)

    # ---------- Flask-Login ----------
    _configure_login_manager(app)

    return app


def _configure_login_manager(app):
    """Configure Flask-Login: view, messages, user loader."""
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to continue.'
    login_manager.login_message_category = 'warning'

    from core.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))


# Module-level app for Flask CLI and WSGI servers.
app = create_app()


def _dev_bootstrap():
    """First-run convenience: seed admin + test catalog if missing.

    Runs only when executing `python app.py` directly.
    For controlled seeding use: flask seed-all
    """
    from core.models import User

    with app.app_context():
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                full_name='System Administrator',
                email='admin@labms.local',
                role='admin',
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('[seed] Default admin created: admin / admin123')
        else:
            print('[seed] Admin already exists - skipping.')

        from modules.tests.seed import seed_tests
        created_tests, created_categories = seed_tests()
        if created_tests or created_categories:
            print(f'Seeded {created_tests} tests and {created_categories} categories.')
        else:
            print('Test catalog already populated — skipping seed.')


if __name__ == '__main__':
    _dev_bootstrap()
    app.run(host='0.0.0.0', port=5000, debug=True)
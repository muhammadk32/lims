from flask import Flask, jsonify, render_template, redirect, url_for
from config import config_map
from extensions import db, login_manager, migrate
from core.logging_config import setup_logging
from core.branding import inject_branding
import os


def create_app(config_name=None):
    """Application factory."""
    config_name = config_name or os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_map[config_name])

    # ---------- Logging ----------
    setup_logging(app)

    # ---------- Initialize extensions ----------
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # ---------- Ensure branding upload folder exists ----------
    upload_dir = os.path.join(app.root_path, 'static', 'uploads', 'branding')
    os.makedirs(upload_dir, exist_ok=True)

    # ---------- Branding context processor ----------
    inject_branding(app)

    # ---------- Context processors ----------
    @app.context_processor
    def inject_globals():
        from flask import request
        return {
            'app_name': app.config.get('APP_NAME', 'LabMS'),
            'app_version': app.config.get('APP_VERSION', '1.0.0'),
            'current_path': request.path,
        }

    @app.context_processor
    def inject_themes():
        from core.themes import THEMES
        return {'themes': THEMES}

    @app.context_processor
    def inject_report_signatures():
        """Make active report signatures available to every template.

        Wrapped in try/except so the app boots even before the
        report_signatures table has been created (first run).
        """
        from core.models import ReportSignature
        try:
            sigs = ReportSignature.active_ordered()
        except Exception:
            sigs = []
        return {'report_signatures': sigs}

    @app.context_processor
    def inject_breadcrumbs():
        from flask import request

        if not getattr(request, 'path', '').startswith('/'):
            return {'breadcrumbs': []}

        path = request.path.strip('/')
        if not path or path.startswith('login') or path.startswith('logout'):
            return {'breadcrumbs': []}

        parts = path.split('/')
        crumbs = []
        accumulated = ''
        labels = {
            'patients': 'Patient Directory',
            'tests': 'Lab Tests',
            'orders': 'Patient Registration',
            'results': 'Results',
            'reports': 'Reports',
            'lab': 'Laboratory',
            'verify': 'Pending Verification',
            'billing': 'Cash Summary',
            'users': 'Users',
            'audit': 'Audit Log',
            'profile': 'Profile',
            'new': 'New',
            'edit': 'Edit',
            'settings': 'Settings',
            'branding': 'Branding',
            'report-signatures': 'Report Signatures',
            'formats': 'Formats',
            'categories': 'Categories',
            'units': 'Units',
            'panels': 'Panels',
            'bulk': 'Bulk',
            'reception-form': 'Reception Form',
            'form_settings': 'Reception Form',
        }
        for i, part in enumerate(parts):
            accumulated += '/' + part
            if part.isdigit():
                continue
            label = labels.get(part, part.replace('-', ' ').title())
            is_last = (i == len(parts) - 1)
            crumbs.append({
                'label': label,
                'url': None if is_last else accumulated,
            })

        return {'breadcrumbs': crumbs}

    @app.context_processor
    def inject_lab():
        from core.branding import get_branding
        b = get_branding()
        return {
            'lab': {
                'name': b.lab_name,
                'tagline': b.tagline or '',
                'address': b.address or '',
                'phone': b.phone or '',
                'email': b.email or '',
                'website': b.website or '',
            }
        }

    # ---------- Template filter: local time (Pakistan) ----------
    @app.template_filter('localtime')
    def _localtime_filter(dt, fmt='%Y-%m-%d %H:%M'):
        """Convert a UTC datetime to Pakistan local time for display."""
        if not dt:
            return '—'
        from datetime import timezone
        try:
            from zoneinfo import ZoneInfo
            tz = ZoneInfo('Asia/Karachi')
        except Exception:
            tz = timezone.utc

        try:
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(tz).strftime(fmt)
        except Exception:
            try:
                return dt.strftime(fmt)
            except Exception:
                return '—'

    # ---------- Flask-Login settings ----------
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to continue.'
    login_manager.login_message_category = 'warning'

    # ---------- User loader ----------
    from core.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # ---------- Register all blueprints ----------
    from modules.auth import auth_bp
    from modules.dashboard import dashboard_bp
    from modules.patients import patients_bp
    from modules.tests import tests_bp
    from modules.orders import orders_bp
    from modules.lab import lab_bp
    from modules.results import results_bp
    from modules.reports import reports_bp
    from modules.billing import billing_bp
    from modules.users import users_bp
    from modules.audit import audit_bp
    from modules.settings.routes import settings_bp
    from modules.test_settings import test_settings_bp
    from modules.form_settings import form_settings_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(tests_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(lab_bp)
    app.register_blueprint(results_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(billing_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(audit_bp)
    app.register_blueprint(settings_bp, url_prefix='/settings')
    app.register_blueprint(test_settings_bp)
    app.register_blueprint(form_settings_bp)

    # ---------- Root redirect ----------
    @app.route('/')
    def index():
        from flask_login import current_user
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
        return redirect(url_for('auth.login'))

    # ---------- Health check ----------
    @app.route('/healthz')
    def healthz():
        try:
            db.session.execute(db.text('SELECT 1'))
            db_ok = True
        except Exception:
            db_ok = False

        return jsonify({
            'status': 'ok' if db_ok else 'degraded',
            'db': 'ok' if db_ok else 'error',
            'version': app.config.get('APP_VERSION', '1.0.0'),
        }), 200 if db_ok else 503

    # ---------- Error handlers ----------
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    # ⚠️ TEMPORARILY DISABLED so the real error shows in the browser
    # @app.errorhandler(500)
    # def server_error(e):
    #     return render_template('errors/500.html'), 500

    return app


# ---------- Module-level app for Flask CLI ----------
app = create_app()


# ---------- Seed default admin ----------
def seed_admin():
    from core.models import User

    existing = User.query.filter_by(username='admin').first()
    if existing:
        print('[seed] Admin already exists - skipping.')
        return

    admin = User(
        username='admin',
        full_name='System Administrator',
        email='admin@labms.local',
        role='admin'
    )
    admin.set_password('admin123')

    db.session.add(admin)
    db.session.commit()
    print('[seed] Default admin created: admin / admin123')


# ---------- Entry point ----------
if __name__ == '__main__':
    with app.app_context():
        seed_admin()

        from modules.tests.seed import seed_tests
        created_tests, created_categories = seed_tests()
        if created_tests or created_categories:
            print(f'✅ Seeded {created_tests} tests and {created_categories} categories.')
        else:
            print('ℹ️  Test catalog already populated — skipping seed.')

    app.run(host='0.0.0.0', port=5000, debug=True)
"""Blueprint registration — kept in one place so app.py stays slim."""


def register_blueprints(app):
    """Import and register every feature blueprint."""

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
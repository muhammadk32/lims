"""Error handlers + root/health routes."""
from flask import jsonify, render_template, redirect, url_for
from extensions import db


def register_error_handlers(app):
    """Register HTTP error handlers and the root/health routes."""

    @app.route('/')
    def index():
        from flask_login import current_user
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
        return redirect(url_for('auth.login'))

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

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    # ⚠️ 500 handler intentionally disabled during development so real errors
    # surface in the browser. Re-enable in production:
    # @app.errorhandler(500)
    # def server_error(e):
    #     return render_template('errors/500.html'), 500
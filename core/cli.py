"""Custom Flask CLI commands — replaces the old __main__ seed block."""
import click
from extensions import db


def register_cli(app):
    """Attach CLI commands to the Flask app."""

    @app.cli.command('seed-admin')
    def seed_admin():
        """Create the default admin user if missing."""
        from core.models import User

        existing = User.query.filter_by(username='admin').first()
        if existing:
            click.echo('[seed] Admin already exists - skipping.')
            return

        admin = User(
            username='admin',
            full_name='System Administrator',
            email='admin@labms.local',
            role='admin',
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        click.echo('[seed] Default admin created: admin / admin123')

    @app.cli.command('seed-tests')
    def seed_tests_cmd():
        """Populate the test catalog with default tests and categories."""
        from modules.tests.seed import seed_tests

        created_tests, created_categories = seed_tests()
        if created_tests or created_categories:
            click.echo(f'Seeded {created_tests} tests and {created_categories} categories.')
        else:
            click.echo('Test catalog already populated — skipping seed.')

    @app.cli.command('seed-all')
    def seed_all():
        """Run every seed step in order."""
        seed_admin.callback()
        seed_tests_cmd.callback()
"""Template context processors — inject shared data into every template."""
from flask import request


def register_context_processors(app):
    """Register all context processors on the Flask app."""

    @app.context_processor
    def inject_globals():
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
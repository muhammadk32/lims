"""
Branding helper — makes the current lab settings available
inside every template automatically (via a context processor).

Falls back to the static constants in modules/reports/pdf_generator.py
if the DB row doesn't exist yet (fresh install).
"""
from core.models import LabSettings


def _fallback_branding():
    """Return a LabSettings instance populated from static constants."""
    try:
        from modules.reports.pdf_generator import (
            LAB_NAME, LAB_TAGLINE, LAB_ADDRESS,
            LAB_PHONE, LAB_EMAIL, LAB_WEBSITE,
        )
    except Exception:
        LAB_NAME = 'Laboratory Management System'
        LAB_TAGLINE = ''
        LAB_ADDRESS = ''
        LAB_PHONE = ''
        LAB_EMAIL = ''
        LAB_WEBSITE = ''

    return LabSettings(
        lab_name=LAB_NAME,
        tagline=LAB_TAGLINE,
        address=LAB_ADDRESS,
        phone=LAB_PHONE,
        email=LAB_EMAIL,
        website=LAB_WEBSITE,
        footer_note='',
        primary_color='#0d6efd',
    )


def get_branding():
    """Return the singleton LabSettings row (creating if needed)."""
    try:
        return LabSettings.get()
    except Exception:
        # Fail-safe for early startup or before migration runs
        return _fallback_branding()


def inject_branding(app):
    """Register a context processor so `branding` is available in all templates."""

    @app.context_processor
    def _inject():
        return {'branding': get_branding()}
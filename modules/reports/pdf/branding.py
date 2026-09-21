"""Lab branding lookup — DB-driven with safe fallbacks."""
import os

from reportlab.lib import colors


_DEFAULT_LAB = {
    'name': 'Laboratory Management System',
    'tagline': '',
    'address': '',
    'phone': '',
    'email': '',
    'website': '',
    'license_no': '',
    'logo_filename': None,
    'logo_path': None,
    'primary_color': '#0d6efd',
    'footer_note': '',
}


def _logo_abs_path(filename):
    """Absolute filesystem path to the logo, or None."""
    if not filename:
        return None
    try:
        from flask import current_app
        path = os.path.join(
            current_app.root_path, 'static', 'uploads', 'branding', filename
        )
        return path if os.path.exists(path) else None
    except Exception:
        return None


def _lab_dict_from_settings(s):
    """Build the lab dict from a LabSettings row."""
    return {
        'name': s.lab_name or _DEFAULT_LAB['name'],
        'tagline': s.tagline or '',
        'address': s.address or '',
        'phone': s.phone or '',
        'email': s.email or '',
        'website': s.website or '',
        'license_no': s.license_no or '',
        'logo_filename': s.logo_filename,
        'logo_path': _logo_abs_path(s.logo_filename),
        'primary_color': s.primary_color or '#0d6efd',
        'footer_note': s.footer_note or '',
    }


def _get_lab():
    """Return current lab branding from DB (or defaults on failure).

    Called fresh every time so branding changes take effect immediately.
    """
    try:
        from flask import has_app_context
        from core.models import LabSettings

        if has_app_context():
            s = LabSettings.get()
            if s:
                return _lab_dict_from_settings(s)

        try:
            from app import app as _app
            with _app.app_context():
                s = LabSettings.get()
                if s:
                    return _lab_dict_from_settings(s)
        except Exception:
            pass

    except Exception as e:
        print(f'[pdf.branding] _get_lab failed: {e}')

    return dict(_DEFAULT_LAB)


def _hex(color_str, fallback='#0d6efd'):
    """Safely convert hex string to reportlab color."""
    try:
        return colors.HexColor(color_str or fallback)
    except Exception:
        return colors.HexColor(fallback)


# ----- Backwards-compat module constants -----
# NOTE: These are resolved once at import. They exist only so other
# modules that do `from ...pdf_generator import LAB_NAME` keep working.
# PDF rendering itself always calls _get_lab() fresh, so branding
# changes appear on the next generated PDF without restart.
_initial = _get_lab()
LAB_NAME = _initial['name']
LAB_TAGLINE = _initial['tagline']
LAB_ADDRESS = _initial['address']
LAB_PHONE = _initial['phone']
LAB_EMAIL = _initial['email']
LAB_WEBSITE = _initial['website']

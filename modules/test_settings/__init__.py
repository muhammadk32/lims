"""
Lab Test Settings module.

Provides admin-only configuration for:
  - Test formats (numeric, qualitative, PCR, etc.)
  - Test categories
  - Units & reference ranges
  - Panel templates (parent/child tests)
  - Bulk import / export

Blueprint: test_settings_bp
URL prefix: /settings/tests
"""
from flask import Blueprint


test_settings_bp = Blueprint(
    'test_settings',
    __name__,
    url_prefix='/settings/tests',
    # No template_folder here — templates resolve from the app's default
    # `templates/` folder. All our templates live at:
    #   templates/test_settings/*.html
)


from . import routes  # noqa: E402,F401
"""
Reception Form Settings module.

Admin-only UI for customizing the reception/order form:
  - Toggle which fields are visible
  - Mark fields required / optional
  - Override labels and default values
  - Toggle entire sections
  - Apply preset profiles

Blueprint: form_settings_bp
URL prefix: /settings/reception-form
"""
from flask import Blueprint


form_settings_bp = Blueprint(
    'form_settings',
    __name__,
    url_prefix='/settings/reception-form',
)


from . import routes  # noqa: E402,F401
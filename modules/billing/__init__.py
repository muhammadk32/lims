from flask import Blueprint

billing_bp = Blueprint(
    'billing',
    __name__,
    url_prefix='/billing',
    template_folder='templates'
)

from . import routes  # noqa: E402,F401
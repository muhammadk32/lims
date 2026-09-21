from flask import Blueprint

lab_bp = Blueprint(
    'lab',
    __name__,
    url_prefix='/lab',
    template_folder='templates'
)

from . import routes  # noqa: E402,F401
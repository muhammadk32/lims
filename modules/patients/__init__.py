from flask import Blueprint

patients_bp = Blueprint(
    'patients',
    __name__,
    url_prefix='/patients',
    template_folder='templates'
)

from . import routes  # noqa: E402,F401
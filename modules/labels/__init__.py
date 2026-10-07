"""Sample barcode labels module."""
from flask import Blueprint

labels_bp = Blueprint(
    'labels',
    __name__,
    url_prefix='/labels',
    template_folder='templates',
)

from . import routes  # noqa: E402,F401

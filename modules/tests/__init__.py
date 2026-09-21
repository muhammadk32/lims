"""
Lab Tests module.

Exposes:
- tests_bp             → Flask blueprint for /tests routes
- Test, TestCategory,
  PanelParameter       → models (for cross-module imports)
- RESULT_FORMATS       → list of (key, label) tuples
- RESULT_FORMAT_KEYS   → list of valid keys
- RESULT_FORMAT_MAP    → dict of key → label
"""
from flask import Blueprint


tests_bp = Blueprint(
    'tests',
    __name__,
    url_prefix='/tests',
    template_folder='templates',
)


# ---------- Re-export models & constants for convenience ----------
from .models import (                                    # noqa: E402,F401
    Test,
    TestCategory,
    PanelParameter,
    RESULT_FORMATS,
    RESULT_FORMAT_KEYS,
    RESULT_FORMAT_MAP,
)

from . import routes  # noqa: E402,F401
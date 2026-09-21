"""Backwards-compat shim.

Real code lives in modules/reports/pdf/*. This file re-exports the
public API and the legacy module-level LAB_* constants so that
existing imports keep working unchanged.
"""
from .pdf.base import TIMEZONE_NAME, _now, _fmt_dt, _fmt_dt_pretty  # noqa: F401
from .pdf.branding import (  # noqa: F401
    _DEFAULT_LAB, _logo_abs_path, _lab_dict_from_settings, _get_lab, _hex,
    LAB_NAME, LAB_TAGLINE, LAB_ADDRESS, LAB_PHONE, LAB_EMAIL, LAB_WEBSITE,
)
from .pdf.header import _header_table, _logo_flowable  # noqa: F401
from .pdf.patient_box import _patient_info_table  # noqa: F401
from .pdf.results_table import _results_table, _flag_result  # noqa: F401
from .pdf.footer import (  # noqa: F401
    BOTTOM_PANEL_HEIGHT, _draw_page_bottom, _footer_flowables,
    _get_active_signatures,
)
from .pdf.generator import generate_report_pdf  # noqa: F401

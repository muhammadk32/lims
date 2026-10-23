from . import base  # noqa: F401 — installs Paragraph sanitizer
"""PDF report package — re-exports the public API."""
from .generator import generate_report_pdf  # noqa: F401

__all__ = ['generate_report_pdf']

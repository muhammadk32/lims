"""Shared constants + timezone helpers for PDF generation."""
from datetime import datetime
from zoneinfo import ZoneInfo

TIMEZONE_NAME = 'Asia/Karachi'


def _now():
    """Current time in the lab timezone."""
    try:
        from flask import current_app
        tz_name = current_app.config.get('TIMEZONE', TIMEZONE_NAME)
    except Exception:
        tz_name = TIMEZONE_NAME

    try:
        return datetime.now(ZoneInfo(tz_name))
    except Exception:
        return datetime.now()


def _fmt_dt(dt, fmt='%Y-%m-%d %H:%M'):
    """Format a datetime in local timezone."""
    if not dt:
        return '—'
    try:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo('UTC'))
        return dt.astimezone(ZoneInfo(TIMEZONE_NAME)).strftime(fmt)
    except Exception:
        try:
            return dt.strftime(fmt)
        except Exception:
            return '—'


def _fmt_dt_pretty(dt):
    """Pretty-format a datetime in the lab timezone (e.g. 19-Sep-2026 01:11 PM)."""
    if not dt:
        return None
    try:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo('UTC'))
        return dt.astimezone(ZoneInfo(TIMEZONE_NAME)).strftime('%d-%b-%Y %I:%M %p')
    except Exception:
        try:
            return dt.strftime('%d-%b-%Y %I:%M %p')
        except Exception:
            return None

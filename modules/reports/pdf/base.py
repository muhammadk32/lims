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

import re as _re
from reportlab.platypus import Paragraph as _RLParagraph

def _sanitize_para_global(html):
    if not html:
        return html
    s = str(html)
    # empty <p> with only brs/whitespace → remove
    s = _re.sub(r'<p>\s*(?:<br\s*/?>\s*)*</p>', '', s, flags=_re.I)
    # trailing brs before </p>
    s = _re.sub(r'(?:<br\s*/?>\s*)+</p>', '</p>', s, flags=_re.I)
    # leading brs after <p>
    s = _re.sub(r'<p>\s*(?:<br\s*/?>\s*)+', '<p>', s, flags=_re.I)
    # collapse 3+ brs to one
    s = _re.sub(r'(?:<br\s*/?>\s*){3,}', '<br/>', s, flags=_re.I)
    # FULL html strip — range/notes text is display-only; no styling needed
    import re as _r2
    # preserve a handful of allowed tags
    _allowed = ('b','i','u','br','sub','sup','font')
    def _strip_bad(m):
        t = m.group(1).lower().split()[0].strip('/')
        return m.group(0) if t in _allowed else ''
    s = _r2.sub(r'<([a-zA-Z][^>]*)>', _strip_bad, s)
    # now close/balance and strip stray <para>
    # strip stray <para>...</para> (reportlab doesn't understand these, treats as unclosed)
    s = _re.sub(r'</?para[^>]*>', '', s, flags=_re.I)
    # bare br not inside p (rare)
    s = _re.sub(r'<br\s*/?>', '<br/>', s, flags=_re.I)
    return s

_orig_rl_paragraph_init = _RLParagraph.__init__
def _patched_paragraph_init(self, text, style, *args, **kwargs):
    if isinstance(text, str):
        text = _sanitize_para_global(text)
    return _orig_rl_paragraph_init(self, text, style, *args, **kwargs)
_RLParagraph.__init__ = _patched_paragraph_init
print('[pdf-base] paragraph sanitizer installed')

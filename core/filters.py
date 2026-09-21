"""Jinja template filters."""


def register_filters(app):
    """Register all custom Jinja filters."""

    @app.template_filter('localtime')
    def _localtime_filter(dt, fmt='%Y-%m-%d %H:%M'):
        """Convert a UTC datetime to Pakistan local time for display."""
        if not dt:
            return '—'
        from datetime import timezone
        try:
            from zoneinfo import ZoneInfo
            tz = ZoneInfo('Asia/Karachi')
        except Exception:
            tz = timezone.utc

        try:
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(tz).strftime(fmt)
        except Exception:
            try:
                return dt.strftime(fmt)
            except Exception:
                return '—'
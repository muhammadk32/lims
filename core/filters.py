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

    @app.template_filter('money')
    def _money_filter(value, decimals=2):
        """Format a number as money: '<currency> 1,234.56'.

        Reads the currency symbol from app config (APP_CURRENCY).
        Empty string = no symbol, just the number.
        """
        if value is None or value == '':
            return '—'
        try:
            num = float(value)
        except (ValueError, TypeError):
            return str(value)

        symbol = app.config.get('APP_CURRENCY', '') or ''
        formatted = f'{num:,.{decimals}f}'
        return f'{symbol} {formatted}' if symbol else formatted
"""
Theme definitions for LabMS.

Each theme has:
  - key:      string stored in User.theme (must match <html data-bs-theme="...">)
  - label:    human-readable name shown in the picker
  - icon:     bootstrap-icons class shown next to the label
  - preview:  hex color or CSS gradient used for the swatch in the picker

Notes:
  - 'light' and 'dark' are handled natively by Bootstrap 5.3.
  - 'auto' is resolved by JavaScript (follows the OS preference).
  - 'grey', 'blue', 'green', 'purple', 'high_contrast' are custom themes
    defined in static/css/themes.css.
"""

THEMES = [
    {
        'key': 'light',
        'label': 'Light',
        'icon': 'bi-sun',
        'preview': '#f8f9fa',
    },
    {
        'key': 'dark',
        'label': 'Dark',
        'icon': 'bi-moon-stars',
        'preview': '#1e293b',
    },
    {
        'key': 'auto',
        'label': 'Auto (follows system)',
        'icon': 'bi-circle-half',
        'preview': 'linear-gradient(90deg, #f8f9fa 50%, #1e293b 50%)',
    },
    {
        'key': 'grey',
        'label': 'Grey',
        'icon': 'bi-circle',
        'preview': '#6b7280',
    },
    {
        'key': 'blue',
        'label': 'Ocean Blue',
        'icon': 'bi-droplet',
        'preview': '#2563eb',
    },
    {
        'key': 'green',
        'label': 'Medical Green',
        'icon': 'bi-heart-pulse',
        'preview': '#059669',
    },
    {
        'key': 'purple',
        'label': 'Royal Purple',
        'icon': 'bi-gem',
        'preview': '#7c3aed',
    },
    {
        'key': 'high_contrast',
        'label': 'High Contrast',
        'icon': 'bi-eye',
        'preview': '#000000',
    },
]

# Quick lookup helpers
THEME_KEYS = [t['key'] for t in THEMES]
THEME_MAP = {t['key']: t for t in THEMES}

DEFAULT_THEME = 'light'


def is_valid_theme(key: str) -> bool:
    """Return True if the given key is a known theme."""
    return key in THEME_KEYS


def get_theme(key: str) -> dict:
    """Return the theme dict for a key, or the default theme."""
    return THEME_MAP.get(key, THEME_MAP[DEFAULT_THEME])
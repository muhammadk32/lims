from functools import wraps
from flask import abort, flash, redirect, url_for, request, jsonify
from flask_login import current_user
from core.roles import has_permission, Role


# ============================================================
# Role-based decorators
# ============================================================
def role_required(*roles):
    """Allow only the listed roles."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return wrapper
    return decorator


def admin_required(f):
    """Shortcut: admin only."""
    return role_required(Role.ADMIN)(f)


# ============================================================
# Permission-based decorator
# ============================================================
def permission_required(permission: str):
    """Allow roles that have the given permission."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                # AJAX requests should get 401/redirect JSON, not HTML
                if _wants_json():
                    return jsonify({'ok': False, 'error': 'Not authenticated'}), 401
                return redirect(url_for('auth.login'))

            if not has_permission(current_user.role, permission):
                if _wants_json():
                    return jsonify({'ok': False, 'error': 'Forbidden'}), 403
                flash('You do not have permission to do that.', 'danger')
                abort(403)

            return f(*args, **kwargs)
        return wrapper
    return decorator


def manage_test_settings_required(f):
    """
    Shortcut: access to Lab Test Settings section.
    Uses the 'manage_test_settings' permission (admin only by default).
    """
    return permission_required('manage_test_settings')(f)


# ============================================================
# Internal helper
# ============================================================
def _wants_json():
    """
    Return True if the current request expects a JSON response.
    Used to send 401/403 as JSON instead of redirects for AJAX calls.
    """
    # Explicit Accept header
    if request.accept_mimetypes.best == 'application/json':
        return True
    # X-Requested-With: XMLHttpRequest (older pattern)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return True
    # POST/PUT/DELETE with JSON body
    if request.is_json:
        return True
    return False
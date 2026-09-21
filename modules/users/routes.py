from flask import (
    render_template, request, redirect, url_for, flash, abort, jsonify
)
from flask_login import login_required, current_user
from extensions import db
from core.models import User
from core.roles import Role
from core.decorators import admin_required
from core.audit import log_action
from core.themes import THEME_KEYS
from . import users_bp


def _get_user_or_404(user_id):
    u = User.query.get(user_id)
    if not u:
        abort(404)
    return u


# ---------- List users (admin only) ----------
@users_bp.route('/')
@login_required
@admin_required
def list_users():
    q = request.args.get('q', '').strip()
    role_filter = request.args.get('role', '').strip()

    query = User.query
    if q:
        like = f'%{q}%'
        query = query.filter(
            (User.username.ilike(like)) |
            (User.full_name.ilike(like)) |
            (User.email.ilike(like))
        )
    if role_filter in Role.CHOICES:
        query = query.filter(User.role == role_filter)

    users = query.order_by(User.id.desc()).all()

    return render_template(
        'users/list.html',
        users=users,
        q=q,
        role_filter=role_filter,
        roles=Role.CHOICES,
        role_labels=Role.LABELS,
    )


# ---------- Create user (admin only) ----------
@users_bp.route('/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_user():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        full_name = request.form.get('full_name', '').strip()
        password = request.form.get('password', '')

        # Validation
        errors = []
        if not username:
            errors.append('Username is required.')
        if not full_name:
            errors.append('Full name is required.')
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        if User.query.filter_by(username=username).first():
            errors.append(f'Username "{username}" already exists.')

        email = request.form.get('email', '').strip() or None
        if email and User.query.filter_by(email=email).first():
            errors.append(f'Email "{email}" is already in use.')

        role = request.form.get('role', Role.TECHNICIAN)
        if role not in Role.CHOICES:
            errors.append('Invalid role selected.')

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('users/form.html',
                                   user=None,
                                   form=request.form,
                                   roles=Role.CHOICES,
                                   role_labels=Role.LABELS)

        user = User(
            username=username,
            full_name=full_name,
            email=email,
            role=role,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        log_action('create', 'user', user.id, f'Created user {user.username} ({user.role})')

        flash(f'User "{user.username}" created.', 'success')
        return redirect(url_for('users.list_users'))

    return render_template('users/form.html',
                           user=None,
                           form={},
                           roles=Role.CHOICES,
                           role_labels=Role.LABELS)


# ---------- Edit user (admin only) ----------
@users_bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = _get_user_or_404(user_id)

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip() or None
        role = request.form.get('role', user.role)

        errors = []
        if not username:
            errors.append('Username is required.')
        if not full_name:
            errors.append('Full name is required.')

        # Uniqueness excluding self
        dup_user = User.query.filter(User.username == username, User.id != user.id).first()
        if dup_user:
            errors.append(f'Username "{username}" is already taken.')
        if email:
            dup_email = User.query.filter(User.email == email, User.id != user.id).first()
            if dup_email:
                errors.append(f'Email "{email}" is already in use.')

        if role not in Role.CHOICES:
            errors.append('Invalid role.')

        # Prevent demoting the last admin
        if user.role == Role.ADMIN and role != Role.ADMIN:
            remaining_admins = User.query.filter(
                User.role == Role.ADMIN, User.id != user.id
            ).count()
            if remaining_admins == 0:
                errors.append('Cannot change the only admin\'s role.')

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('users/form.html',
                                   user=user,
                                   form=request.form,
                                   roles=Role.CHOICES,
                                   role_labels=Role.LABELS)

        user.username = username
        user.full_name = full_name
        user.email = email
        user.role = role
        db.session.commit()

        log_action('update', 'user', user.id, f'Updated user {user.username}')

        flash(f'User "{user.username}" updated.', 'success')
        return redirect(url_for('users.list_users'))

    return render_template('users/form.html',
                           user=user,
                           form={},
                           roles=Role.CHOICES,
                           role_labels=Role.LABELS)


# ---------- Reset password (admin only) ----------
@users_bp.route('/<int:user_id>/reset-password', methods=['POST'])
@login_required
@admin_required
def reset_password(user_id):
    user = _get_user_or_404(user_id)
    new_pass = request.form.get('new_password', '')

    if not new_pass or len(new_pass) < 6:
        flash('Password must be at least 6 characters.', 'danger')
    else:
        user.set_password(new_pass)
        db.session.commit()

        log_action('update', 'user', user.id, f'Reset password for {user.username}')

        flash(f'Password reset for "{user.username}".', 'success')

    return redirect(url_for('users.list_users'))


# ---------- Toggle active (admin only) ----------
@users_bp.route('/<int:user_id>/toggle-active', methods=['POST'])
@login_required
@admin_required
def toggle_active(user_id):
    user = _get_user_or_404(user_id)

    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'danger')
        return redirect(url_for('users.list_users'))

    # Prevent deactivating last admin
    if user.role == Role.ADMIN and user.is_active_flag:
        remaining = User.query.filter(
            User.role == Role.ADMIN,
            User.id != user.id,
            User.is_active_flag == True,
        ).count()
        if remaining == 0:
            flash('Cannot deactivate the only active admin.', 'danger')
            return redirect(url_for('users.list_users'))

    user.is_active_flag = not user.is_active_flag
    db.session.commit()

    log_action('update', 'user', user.id,
               f'{"Activated" if user.is_active_flag else "Deactivated"} {user.username}')

    state = 'activated' if user.is_active_flag else 'deactivated'
    flash(f'User "{user.username}" {state}.', 'info')
    return redirect(url_for('users.list_users'))


# ---------- Own profile (any logged-in user) ----------
@users_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        action = request.form.get('action', '')

        if action == 'update_info':
            full_name = request.form.get('full_name', '').strip()
            email = request.form.get('email', '').strip() or None

            errors = []
            if not full_name:
                errors.append('Full name is required.')
            if email:
                dup = User.query.filter(User.email == email, User.id != current_user.id).first()
                if dup:
                    errors.append('That email is already in use.')

            if errors:
                for e in errors:
                    flash(e, 'danger')
            else:
                current_user.full_name = full_name
                current_user.email = email
                db.session.commit()

                log_action('update', 'user', current_user.id, 'Updated own profile')

                flash('Profile updated.', 'success')

        elif action == 'change_password':
            old = request.form.get('old_password', '')
            new = request.form.get('new_password', '')
            confirm = request.form.get('confirm_password', '')

            if not current_user.check_password(old):
                flash('Current password is incorrect.', 'danger')
            elif len(new) < 6:
                flash('New password must be at least 6 characters.', 'danger')
            elif new != confirm:
                flash('Passwords do not match.', 'danger')
            else:
                current_user.set_password(new)
                db.session.commit()

                log_action('update', 'user', current_user.id, 'Changed own password')

                flash('Password changed successfully.', 'success')

        return redirect(url_for('users.profile'))

    return render_template('users/profile.html', roles=Role.CHOICES, role_labels=Role.LABELS)


# ---------- Set theme (any logged-in user) ----------   # ← NEW
@users_bp.route('/theme', methods=['POST'])
@login_required
def set_theme():
    """Save the user's chosen theme to the DB."""
    data = request.get_json(silent=True) or {}
    theme = (data.get('theme') or '').strip()

    if theme not in THEME_KEYS:
        return jsonify({'ok': False, 'error': 'Invalid theme'}), 400

    current_user.theme = theme
    db.session.commit()

    try:
        log_action('update', 'user', current_user.id, f'Changed theme to {theme}')
    except Exception:
        pass  # never fail the theme change because of audit log

    return jsonify({'ok': True, 'theme': theme})
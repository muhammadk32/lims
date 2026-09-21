from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from core.models import User
from core.audit import log_action
from . import auth_bp


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # If already logged in, skip login page
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account is disabled. Contact the administrator.', 'danger')
                return render_template('auth/login.html')

            from datetime import datetime
            from extensions import db

            user.last_login = datetime.utcnow()
            db.session.commit()

            login_user(user, remember=bool(request.form.get('remember')))

            log_action('login', 'user', user.id, f'User {user.username} logged in')

            flash(f'Welcome back, {user.full_name}!', 'success')

            # Safe redirect: only allow same-site next URLs
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('dashboard.index'))

        flash('Invalid username or password.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    log_action('logout', 'user', current_user.id, f'User {current_user.username} logged out')

    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
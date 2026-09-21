import os
import uuid

from flask import (
    Blueprint, render_template, redirect, url_for, flash,
    current_app, request,
)
from flask_login import login_required, current_user

from extensions import db
from core.models import LabSettings
from modules.settings.forms import BrandingForm

settings_bp = Blueprint(
    'settings',
    __name__,
    template_folder='../../templates/settings',
)

ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'svg', 'webp'}


def _admin_only():
    """Return True if current user may edit branding."""
    if not current_user.is_authenticated:
        return False
    # Your User.role is a plain string → has_role('admin') works
    return current_user.has_role('admin')


@settings_bp.route('/branding', methods=['GET', 'POST'])
@login_required
def branding():
    if not _admin_only():
        flash('Only administrators can edit branding.', 'danger')
        return redirect(url_for('dashboard.index'))

    settings = LabSettings.get()
    form = BrandingForm(obj=settings)

    if form.validate_on_submit():
        # --- Basic fields ---
        settings.lab_name = (form.lab_name.data or '').strip()
        settings.tagline = form.tagline.data or ''
        settings.address = form.address.data or ''
        settings.phone = form.phone.data or ''
        settings.email = form.email.data or ''
        settings.website = form.website.data or ''
        settings.license_no = form.license_no.data or ''
        settings.footer_note = form.footer_note.data or ''
        settings.primary_color = (form.primary_color.data or '#0d6efd').strip()

        # --- Logo upload ---
        file = request.files.get('logo')
        if file and file.filename:
            ext = file.filename.rsplit('.', 1)[-1].lower()
            if ext not in ALLOWED_EXT:
                flash('Unsupported file type. Use png/jpg/svg/webp.', 'danger')
                return render_template('branding.html', form=form, settings=settings)

            # Delete old logo
            if settings.logo_filename:
                old_path = os.path.join(
                    current_app.root_path, 'static', 'uploads', 'branding',
                    settings.logo_filename,
                )
                if os.path.exists(old_path):
                    try:
                        os.remove(old_path)
                    except OSError:
                        pass

            # Save new logo with unique name
            new_name = f'logo_{uuid.uuid4().hex[:12]}.{ext}'
            save_dir = os.path.join(
                current_app.root_path, 'static', 'uploads', 'branding'
            )
            os.makedirs(save_dir, exist_ok=True)
            file.save(os.path.join(save_dir, new_name))
            settings.logo_filename = new_name

        db.session.commit()
        flash('Branding updated successfully.', 'success')
        return redirect(url_for('settings.branding'))

    return render_template('branding.html', form=form, settings=settings)


@settings_bp.route('/branding/remove-logo', methods=['POST'])
@login_required
def remove_logo():
    if not _admin_only():
        flash('Not allowed.', 'danger')
        return redirect(url_for('dashboard.index'))

    settings = LabSettings.get()
    if settings.logo_filename:
        old_path = os.path.join(
            current_app.root_path, 'static', 'uploads', 'branding',
            settings.logo_filename,
        )
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
            except OSError:
                pass
        settings.logo_filename = None
        db.session.commit()
        flash('Logo removed.', 'info')

    return redirect(url_for('settings.branding'))
# ============================================================
# REPORT SIGNATURES — panel of doctors/staff on printed reports
# ============================================================
from core.models import ReportSignature


@settings_bp.route('/report-signatures')
@login_required
def report_signatures():
    if not _admin_only():
        flash('Only administrators can manage report signatures.', 'danger')
        return redirect(url_for('dashboard.index'))

    sigs = ReportSignature.query.order_by(
        ReportSignature.sort_order, ReportSignature.id
    ).all()
    return render_template('report_signatures.html', signatures=sigs)


@settings_bp.route('/report-signatures/create', methods=['POST'])
@login_required
def report_signature_create():
    if not _admin_only():
        return {'ok': False, 'error': 'Not allowed'}, 403

    name = (request.form.get('name') or '').strip()
    quals = (request.form.get('qualifications') or '').strip()
    desig = (request.form.get('designation') or '').strip()

    if not name:
        flash('Name is required.', 'danger')
        return redirect(url_for('settings.report_signatures'))

    # Place new signature at end
    max_order = db.session.query(
        db.func.coalesce(db.func.max(ReportSignature.sort_order), 0)
    ).scalar()

    sig = ReportSignature(
        name=name,
        qualifications=quals or None,
        designation=desig or None,
        sort_order=max_order + 1,
        is_active=True,
    )
    db.session.add(sig)
    db.session.commit()

    flash(f'Signature "{name}" added.', 'success')
    return redirect(url_for('settings.report_signatures'))


@settings_bp.route('/report-signatures/<int:sig_id>/update', methods=['POST'])
@login_required
def report_signature_update(sig_id):
    if not _admin_only():
        return {'ok': False, 'error': 'Not allowed'}, 403

    sig = ReportSignature.query.get_or_404(sig_id)

    name = (request.form.get('name') or '').strip()
    quals = (request.form.get('qualifications') or '').strip()
    desig = (request.form.get('designation') or '').strip()

    if not name:
        flash('Name is required.', 'danger')
        return redirect(url_for('settings.report_signatures'))

    sig.name = name
    sig.qualifications = quals or None
    sig.designation = desig or None
    db.session.commit()

    flash(f'Signature "{name}" updated.', 'success')
    return redirect(url_for('settings.report_signatures'))


@settings_bp.route('/report-signatures/<int:sig_id>/toggle', methods=['POST'])
@login_required
def report_signature_toggle(sig_id):
    if not _admin_only():
        return {'ok': False, 'error': 'Not allowed'}, 403

    sig = ReportSignature.query.get_or_404(sig_id)
    sig.is_active = not sig.is_active
    db.session.commit()

    flash(
        f'Signature "{sig.name}" {"shown" if sig.is_active else "hidden"}.',
        'info',
    )
    return redirect(url_for('settings.report_signatures'))


@settings_bp.route('/report-signatures/<int:sig_id>/delete', methods=['POST'])
@login_required
def report_signature_delete(sig_id):
    if not _admin_only():
        return {'ok': False, 'error': 'Not allowed'}, 403

    sig = ReportSignature.query.get_or_404(sig_id)
    name = sig.name
    db.session.delete(sig)
    db.session.commit()

    flash(f'Signature "{name}" deleted.', 'info')
    return redirect(url_for('settings.report_signatures'))


@settings_bp.route('/report-signatures/<int:sig_id>/move/<direction>', methods=['POST'])
@login_required
def report_signature_move(sig_id, direction):
    if not _admin_only():
        return {'ok': False, 'error': 'Not allowed'}, 403

    sig = ReportSignature.query.get_or_404(sig_id)

    if direction == 'up':
        other = (
            ReportSignature.query
            .filter(ReportSignature.sort_order < sig.sort_order)
            .order_by(ReportSignature.sort_order.desc())
            .first()
        )
    elif direction == 'down':
        other = (
            ReportSignature.query
            .filter(ReportSignature.sort_order > sig.sort_order)
            .order_by(ReportSignature.sort_order.asc())
            .first()
        )
    else:
        other = None

    if other:
        sig.sort_order, other.sort_order = other.sort_order, sig.sort_order
        db.session.commit()

    return redirect(url_for('settings.report_signatures'))
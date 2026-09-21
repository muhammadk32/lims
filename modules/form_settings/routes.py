"""
Reception Form Settings — routes.

All routes are admin-only via 'manage_test_settings' permission
(shared with Lab Test Settings for consistency).
"""
from flask import (
    render_template, request, redirect, url_for, flash, jsonify,
)
from flask_login import login_required, current_user

from extensions import db
from core.decorators import manage_test_settings_required
from core.models import FormFieldConfig, FormSectionConfig
from core.form_fields import (
    FORM_SECTIONS, FORM_FIELDS, PRESETS, get_section_label, get_field_definitions,
)
from . import form_settings_bp


# ============================================================
# Permission guard
# ============================================================
@form_settings_bp.before_request
@login_required
@manage_test_settings_required
def _guard():
    return None


# ============================================================
# Main page
# ============================================================
@form_settings_bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return _handle_save()

    # ---------- Load current config ----------
    field_configs = {c.field_key: c for c in FormFieldConfig.query.all()}
    section_configs = {c.section_key: c for c in FormSectionConfig.query.all()}
    definitions = get_field_definitions()

    # ---------- Build sections data for template ----------
    sections = []
    for section_key, section_label in FORM_SECTIONS:
        section_cfg = section_configs.get(section_key)
        is_visible = section_cfg.is_visible if section_cfg else True

        # Fields in this section
        fields = []
        for key, defn in definitions.items():
            if defn['section'] != section_key:
                continue
            cfg = field_configs.get(key)
            fields.append({
                'key': key,
                'label': defn['label'],
                'input_type': defn['input_type'],
                'is_visible': cfg.is_visible if cfg else defn['default_visible'],
                'is_required': cfg.is_required if cfg else defn['default_required'],
                'custom_label': cfg.custom_label if cfg else None,
                'default_value': cfg.default_value if cfg else None,
                'sort_order': cfg.sort_order if cfg else 0,
            })

        # Sort fields by sort_order
        fields.sort(key=lambda f: f['sort_order'])

        sections.append({
            'key': section_key,
            'label': section_label,
            'is_visible': is_visible,
            'fields': fields,
            'field_count': len(fields),
            'visible_count': sum(1 for f in fields if f['is_visible']),
        })

    # ---------- Stats ----------
    total_fields = FormFieldConfig.query.count()
    visible_fields = FormFieldConfig.query.filter_by(is_visible=True).count()
    required_fields = FormFieldConfig.query.filter_by(is_required=True).count()

    # ---------- Preset list ----------
    preset_list = [
        {'key': k, 'label': v['label'], 'description': v['description']}
        for k, v in PRESETS.items()
    ]

    return render_template(
        'form_settings/index.html',
        sections=sections,
        preset_list=preset_list,
        stats={
            'total': total_fields,
            'visible': visible_fields,
            'required': required_fields,
        },
    )


def _handle_save():
    """Save all field configs from the form submission."""
    # ---------- Section toggles ----------
    section_visible_keys = set(request.form.getlist('section_visible'))

    for section_key, _label in FORM_SECTIONS:
        cfg = FormSectionConfig.query.filter_by(section_key=section_key).first()
        if not cfg:
            continue
        cfg.is_visible = section_key in section_visible_keys

    # ---------- Field configs ----------
    # Form fields come in as:
    #   field_visible_<key>       = checkbox value
    #   field_required_<key>      = checkbox value
    #   field_label_<key>         = text
    #   field_default_<key>       = text
    all_field_keys = set(request.form.getlist('all_field_keys'))

    for field_key in all_field_keys:
        cfg = FormFieldConfig.query.filter_by(field_key=field_key).first()
        if not cfg:
            continue

        visible = f'field_visible_{field_key}' in request.form
        required = f'field_required_{field_key}' in request.form

        # Required implies visible
        if required:
            visible = True

        cfg.is_visible = visible
        cfg.is_required = required

        label = (request.form.get(f'field_label_{field_key}') or '').strip()
        cfg.custom_label = label or None

        default = (request.form.get(f'field_default_{field_key}') or '').strip()
        cfg.default_value = default or None

    db.session.commit()
    flash('Reception form settings saved.', 'success')
    return redirect(url_for('form_settings.index'))


# ============================================================
# Apply preset
# ============================================================
@form_settings_bp.route('/apply-preset/<preset_key>', methods=['POST'])
def apply_preset(preset_key):
    """Reset all field configs according to a preset profile."""
    preset = PRESETS.get(preset_key)
    if not preset:
        flash(f'Unknown preset: {preset_key}', 'danger')
        return redirect(url_for('form_settings.index'))

    overrides = preset.get('fields', {})
    definitions = get_field_definitions()

    for key, defn in definitions.items():
        cfg = FormFieldConfig.query.filter_by(field_key=key).first()
        if not cfg:
            continue

        if key in overrides:
            cfg.is_visible = overrides[key].get('visible', defn['default_visible'])
            cfg.is_required = overrides[key].get('required', defn['default_required'])
        else:
            # Fall back to catalog defaults
            cfg.is_visible = defn['default_visible']
            cfg.is_required = defn['default_required']

        if cfg.is_required:
            cfg.is_visible = True

    # All sections visible by default
    for section_key, _label in FORM_SECTIONS:
        sec = FormSectionConfig.query.filter_by(section_key=section_key).first()
        if sec:
            sec.is_visible = True

    db.session.commit()
    flash(f'Preset "{preset["label"]}" applied.', 'success')
    return redirect(url_for('form_settings.index'))


# ============================================================
# Reset to catalog defaults
# ============================================================
@form_settings_bp.route('/reset-defaults', methods=['POST'])
def reset_defaults():
    """Reset every field to the catalog default."""
    definitions = get_field_definitions()

    for key, defn in definitions.items():
        cfg = FormFieldConfig.query.filter_by(field_key=key).first()
        if not cfg:
            continue
        cfg.is_visible = defn['default_visible']
        cfg.is_required = defn['default_required']
        cfg.custom_label = None
        cfg.default_value = None

    for section_key, _label in FORM_SECTIONS:
        sec = FormSectionConfig.query.filter_by(section_key=section_key).first()
        if sec:
            sec.is_visible = True

    db.session.commit()
    flash('All fields reset to catalog defaults.', 'info')
    return redirect(url_for('form_settings.index'))
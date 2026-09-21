"""
Forms for the Reception Form Settings page.

Because the settings page has many rows (one per field), we don't use
WTForms for the bulk save — we read the POST data manually in routes.py.
This module is reserved for future single-field edit forms if needed.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Optional, Length


class FieldOverrideForm(FlaskForm):
    """Edit a single field's label / default value (used in future)."""
    custom_label = StringField('Custom Label', validators=[Optional(), Length(max=80)])
    default_value = StringField('Default Value', validators=[Optional(), Length(max=255)])
    submit = SubmitField('Save')


class ApplyPresetForm(FlaskForm):
    """Apply a preset profile."""
    preset = StringField('Preset')  # 'simple', 'standard', 'detailed'
    submit = SubmitField('Apply Preset')
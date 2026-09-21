from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Email


class BrandingForm(FlaskForm):
    lab_name = StringField(
        'Laboratory Name',
        validators=[DataRequired(), Length(max=150)],
    )
    tagline = StringField(
        'Tagline (optional)',
        validators=[Optional(), Length(max=200)],
    )

    logo = FileField(
        'Logo',
        validators=[FileAllowed(['png', 'jpg', 'jpeg', 'svg', 'webp'],
                                'Images only (png/jpg/svg/webp)')],
    )

    address = StringField('Address', validators=[Optional(), Length(max=255)])
    phone = StringField('Phone', validators=[Optional(), Length(max=50)])
    email = StringField('Email', validators=[Optional(), Email(), Length(max=120)])
    website = StringField('Website', validators=[Optional(), Length(max=150)])
    license_no = StringField('License No.', validators=[Optional(), Length(max=80)])

    footer_note = StringField(
        'Footer note (printed on reports)',
        validators=[Optional(), Length(max=255)],
    )

    primary_color = StringField(
        'Primary color (hex)',
        validators=[Optional(), Length(max=20)],
    )

    submit = SubmitField('Save Branding')
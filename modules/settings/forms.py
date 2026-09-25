from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SelectField, BooleanField, SubmitField
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

    header_style = SelectField(
        'PDF Header Layout',
        choices=[
            ('centered', 'Centered ? logo top, text below (default)'),
            ('left',     'Left-aligned ? logo top-left, text stacked'),
            ('split',    'Split ? logo left, name + contact right'),
            ('banner',   'Banner only ? logo image, no text below'),
        ],
        default='centered',
    )

    header_logo_size = SelectField(
        'Header logo size',
        choices=[('small','Small'),('medium','Medium'),('large','Large')],
        default='medium',
    )
    header_show_divider = BooleanField('Show divider line under header', default=True)
    header_divider_color = StringField(
        'Divider color (hex ? leave blank to use primary color)',
        validators=[Optional(), Length(max=20)],
    )
    header_show_contact = BooleanField('Show contact info in header', default=True)

    submit = SubmitField('Save Branding')
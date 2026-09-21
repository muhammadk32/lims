"""
WTForms for Lab Test Settings.

Used for:
  - Category create / edit
  - (Future) Unit create / edit
  - (Future) Panel creation / editing
"""
from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, SubmitField, IntegerField, FloatField,
    BooleanField, SelectField, SelectMultipleField, HiddenField,
)
from wtforms.validators import (
    DataRequired, Length, Optional, NumberRange,
)

from modules.tests import RESULT_FORMATS, RESULT_FORMAT_KEYS


# ============================================================
# Test format choices
# ============================================================
FORMAT_CHOICES = [(k, label) for k, label in RESULT_FORMATS]


# ============================================================
# Category form
# ============================================================
class CategoryForm(FlaskForm):
    name = StringField(
        'Category Name',
        validators=[DataRequired(), Length(max=80)],
    )
    description = StringField(
        'Description',
        validators=[Optional(), Length(max=255)],
    )
    submit = SubmitField('Save Category')


# ============================================================
# Format edit form (used for full-page edit; inline AJAX
# uses JSON instead — kept here for a future bulk-edit UI)
# ============================================================
class TestFormatForm(FlaskForm):
    test_id = HiddenField()
    result_format = SelectField(
        'Result Format',
        choices=FORMAT_CHOICES,
        validators=[DataRequired()],
    )
    submit = SubmitField('Save Format')


# ============================================================
# (Phase 4) Panel form — create / edit
# ============================================================
class PanelForm(FlaskForm):
    code = StringField(
        'Panel Code',
        validators=[DataRequired(), Length(max=20)],
    )
    name = StringField(
        'Panel Name',
        validators=[DataRequired(), Length(max=120)],
    )
    category_id = SelectField(
        'Category',
        coerce=int,
        validators=[Optional()],
    )
    price = FloatField(
        'Panel Price',
        validators=[DataRequired(), NumberRange(min=0)],
        default=0.0,
    )
    description = TextAreaField(
        'Description',
        validators=[Optional(), Length(max=2000)],
    )
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Panel')

    def set_category_choices(self, categories):
        """Populate category choices; include a blank option."""
        self.category_id.choices = [(0, '— None —')] + [
            (c.id, c.name) for c in categories
        ]


# ============================================================
# (Phase 4) Panel parameter — just for reference/ordering
# ============================================================
class PanelParameterForm(FlaskForm):
    panel_id = HiddenField()
    test_id = HiddenField()
    sort_order = IntegerField('Order', default=0)
    submit = SubmitField('Add Parameter')


# ============================================================
# (Phase 3) Unit form — placeholder for Phase 3
# ============================================================
class UnitForm(FlaskForm):
    symbol = StringField(
        'Unit Symbol',
        validators=[DataRequired(), Length(max=30)],
    )
    description = StringField(
        'Description',
        validators=[Optional(), Length(max=120)],
    )
    submit = SubmitField('Save Unit')
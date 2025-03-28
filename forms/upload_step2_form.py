from flask_wtf import FlaskForm
from wtforms import (
    SelectField,
    SelectMultipleField,
    StringField,
    FormField,
    FieldList,
)
from wtforms.validators import DataRequired


class NewStrainsForm(FlaskForm):
    class Meta:
        csrf = False

    name        = StringField('name', validators=[DataRequired()])
    description = StringField('description')
    species     = SelectField('species')


class UploadStep2Form(FlaskForm):
    strains     = SelectMultipleField('strains')
    new_strains = FieldList(FormField(NewStrainsForm), min_entries=0)

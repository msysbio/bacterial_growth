from wtforms import (
    SelectField,
    SelectMultipleField,
    StringField,
    FormField,
    FieldList,
)
from wtforms.validators import DataRequired

from forms.base_form import BaseForm


class UploadStep2Form(BaseForm):

    class NewStrainsForm(BaseForm):
        class Meta:
            csrf = False

        name        = StringField('name', validators=[DataRequired()])
        description = StringField('description')
        species     = SelectField('species')

    strains     = SelectMultipleField('strains')
    new_strains = FieldList(FormField(NewStrainsForm), min_entries=0)

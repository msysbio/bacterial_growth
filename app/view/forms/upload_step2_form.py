from wtforms import (
    SelectField,
    SelectMultipleField,
    StringField,
    FormField,
    FieldList,
    TextAreaField,
)
from wtforms.validators import DataRequired

from app.view.forms.base_form import BaseForm


class UploadStep2Form(BaseForm):

    class NewStrainForm(BaseForm):
        class Meta:
            csrf = False

        name        = StringField('name', validators=[DataRequired()])
        description = TextAreaField('description')
        species     = SelectField('species', choices=[], validate_choice=False)

    strains        = SelectMultipleField('strains', choices=[], validate_choice=False)
    custom_strains = FieldList(FormField(NewStrainForm))

    def validate_custom_strains(self, field):
        names = [s['name'] for s in field.data]
        self._validate_uniqueness("Strain names are not unique", names)

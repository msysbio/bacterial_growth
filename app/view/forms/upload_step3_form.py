from wtforms import (
    BooleanField,
    FieldList,
    FormField,
    SelectMultipleField,
    StringField,
)
from wtforms.validators import DataRequired

from app.view.forms.base_form import BaseForm


class UploadStep3Form(BaseForm):

    class TechniqueForm(BaseForm):
        class Meta:
            csrf = False

        type          = StringField('type', validators=[DataRequired()])
        subjectType   = StringField('subjectType', validators=[DataRequired()])
        units         = StringField('units')
        description   = StringField('description')
        includeStd    = BooleanField('includeStd')
        metaboliteIds = SelectMultipleField('metaboliteIds', choices=[], validate_choice=False)

    techniques = FieldList(FormField(TechniqueForm))

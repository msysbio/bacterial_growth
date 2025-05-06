from wtforms import (
    BooleanField,
    DecimalField,
    FieldList,
    FormField,
    SelectField,
    SelectMultipleField,
    StringField,
    TextAreaField,
    URLField,
)
from wtforms.validators import DataRequired

from forms.base_form import BaseForm


class UploadStep5Form(BaseForm):

    class ExperimentForm(BaseForm):
        class Meta:
            csrf = False

        class BioreplicateForm(BaseForm):
            class Meta:
                csrf = False

            name        = StringField('name', validators=[DataRequired()])
            description = StringField('description')

        name        = StringField('name', validators=[DataRequired()])
        description = TextAreaField('description', validators=[DataRequired()])

        cultivationMode = SelectField('cultivationMode', choices=[
            ('batch',     "Batch"),
            ('fed-batch', "Fed-batch"),
            ('chemostat', "Chemostat"),
            ('other',     "Other"),
        ])

        communityName = SelectField(
            'communityName',
            validators=[DataRequired()],
            choices=[],
            validate_choice=False,
        )
        compartmentNames = SelectMultipleField(
            'compartmentNames',
            validators=[DataRequired()],
            choices=[],
            validate_choice=False,
        )

        bioreplicates = FieldList(FormField(BioreplicateForm))

        def validate_bioreplicates(self, field):
            names = [b['name'] for b in field.data]
            self._validate_uniqueness("Bioreplicate names are not unique", names)

    experiments = FieldList(FormField(ExperimentForm))

    def validate_experiments(self, field):
        names = [e['name'] for e in field.data]
        self._validate_uniqueness("Experiment names are not unique", names)

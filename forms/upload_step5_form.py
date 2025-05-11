from wtforms import (
    FieldList,
    FormField,
    IntegerField,
    SelectField,
    SelectMultipleField,
    StringField,
    TextAreaField,
    URLField,
)
from wtforms.validators import DataRequired, ValidationError

from forms.base_form import BaseForm


class UploadStep5Form(BaseForm):

    class ExperimentForm(BaseForm):
        class Meta:
            csrf = False

        class BioreplicateForm(BaseForm):
            class Meta:
                csrf = False

            name         = StringField('name', validators=[DataRequired()])
            description  = StringField('description')
            biosampleUrl = URLField('biosampleUrl')

        class PerturbationForm(BaseForm):
            class Meta:
                csrf = False

            startTimepoint = IntegerField('startTimepoint', validators=[DataRequired()])
            description = TextAreaField('description', validators=[DataRequired()])

            removedCompartmentName = SelectField('removedCompartmentName', choices=[], validate_choice=False)
            addedCompartmentName   = SelectField('addedCompartmentName',   choices=[], validate_choice=False)
            oldCommunityName       = SelectField('oldCommunityName',       choices=[], validate_choice=False)
            newCommunityName       = SelectField('newCommunityName',       choices=[], validate_choice=False)

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
        perturbations = FieldList(FormField(PerturbationForm))

        def validate_bioreplicates(self, field):
            names = [b['name'] for b in field.data]
            self._validate_uniqueness("names are not unique", names)

            if len(names) == 0:
                raise ValidationError("at least one is required")

    experiments = FieldList(FormField(ExperimentForm))

    def validate_experiments(self, field):
        # Local validation:
        names = [e['name'] for e in field.data]
        self._validate_uniqueness("names are not unique", names)

        # Global bioreplicate validation:
        names = [
            bioreplicate['name']
            for experiment in field.data
            for bioreplicate in experiment['bioreplicates']
        ]
        self._validate_uniqueness("bioreplicate names are not globally unique", names)

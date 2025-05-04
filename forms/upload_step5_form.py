from flask_wtf import FlaskForm
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


class UploadStep5Form(FlaskForm):

    class ExperimentForm(FlaskForm):
        class Meta:
            csrf = False

        class BioreplicateForm(FlaskForm):
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

        communityName    = SelectField('communityName')
        compartmentNames = SelectMultipleField('compartmentNames')

        bioreplicates = FieldList(FormField(BioreplicateForm))

        def get_bioreplicate_template(self):
            return self.__class__.BioreplicateForm()

    experiments = FieldList(FormField(ExperimentForm))

    def get_experiment_template(self):
        return self.__class__.ExperimentForm()

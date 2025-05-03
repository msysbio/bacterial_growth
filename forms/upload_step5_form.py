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

        name        = StringField('name', validators=[DataRequired()])
        description = TextAreaField('description')

    experiments = FieldList(FormField(ExperimentForm))

    def get_experiment_template(self):
        return self.__class__.ExperimentForm()

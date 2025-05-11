from wtforms import (
    BooleanField,
    DecimalField,
    FieldList,
    FormField,
    SelectField,
    SelectMultipleField,
    StringField,
    URLField,
)
from wtforms.validators import DataRequired, Optional

from forms.base_form import BaseForm


class UploadStep4Form(BaseForm):

    class CompartmentForm(BaseForm):
        class Meta:
            csrf = False

        name = StringField('name', validators=[DataRequired()])

        mediumName = StringField('mediumName')
        mediumUrl  = URLField('mediumUrl')

        volume        = DecimalField('volume',        validators=[Optional()])
        pressure      = DecimalField('pressure',      validators=[Optional()])
        stirringSpeed = DecimalField('stirringSpeed', validators=[Optional()])

        stirringMode = SelectField('stirringMode', choices=[
            ('',            ""),
            ('linear',      "Linear"),
            ('orbital',     "Orbital"),
            ('vibrational', "Vibrational"),
        ])

        O2  = DecimalField('O2',  validators=[Optional()])
        CO2 = DecimalField('CO2', validators=[Optional()])
        H2  = DecimalField('H2',  validators=[Optional()])
        N2  = DecimalField('N2',  validators=[Optional()])

        inoculumConcentration = DecimalField('inoculumConcentration', validators=[Optional()], places=3)
        inoculumVolume        = DecimalField('inoculumVolume',        validators=[Optional()])

        initialPh          = DecimalField('initialPh',          validators=[Optional()])
        initialTemperature = DecimalField('initialTemperature', validators=[Optional()])

        carbonSource = BooleanField('carbonSource')

    class CommunityForm(BaseForm):
        class Meta:
            csrf = False

        name              = StringField('name', validators=[DataRequired()])
        strainIdentifiers = SelectMultipleField('strainIdentifiers', choices=[], validate_choice=False)

    compartments = FieldList(FormField(CompartmentForm))
    communities  = FieldList(FormField(CommunityForm))

    def validate_compartments(self, field):
        names = [c['name'] for c in field.data]
        self._validate_uniqueness("Compartment names are not unique", names)

    def validate_communities(self, field):
        names = [c['name'] for c in field.data]
        self._validate_uniqueness("Community names are not unique", names)

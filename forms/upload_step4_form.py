from flask_wtf import FlaskForm
from wtforms import (
    SelectField,
    StringField,
    BooleanField,
    FieldList,
    FormField,
    DecimalField,
    URLField,
    TextAreaField,
)
from wtforms.validators import DataRequired


class UploadStep4Form(FlaskForm):

    class CompartmentForm(FlaskForm):
        class Meta:
            csrf = False

        name_       = StringField('name', validators=[DataRequired()])
        description = TextAreaField('description')

        mediumName = StringField('mediumName')
        mediumUrl  = URLField('mediumUrl')

        volume        = DecimalField('volume')
        pressure      = DecimalField('pressure')
        stirringSpeed = DecimalField('stirringSpeed')

        stirringMode = SelectField('stirringMode', choices=[
            ('',            ""),
            ('linear',      "Linear"),
            ('orbital',     "Orbital"),
            ('vibrational', "Vibrational"),
        ])

        O2  = DecimalField('O2')
        CO2 = DecimalField('CO2')
        H2  = DecimalField('H2')
        N2  = DecimalField('N2')

        inoculumConcentration = DecimalField('inoculumConcentration', places=3)
        inoculumVolume        = DecimalField('inoculumVolume')

        initialPh          = DecimalField('initialPh')
        initialTemperature = DecimalField('initialTemperature')

        carbonSource = BooleanField('carbonSource')

    compartments = FieldList(FormField(CompartmentForm))

    def get_compartment_template(self):
        return self.__class__.CompartmentForm()

from flask_wtf import FlaskForm
from wtforms import SelectField, SelectMultipleField, IntegerField
from wtforms.validators import DataRequired

# TODO (2024-09-30) Extract types of vessels etc into enums in the database for easy model lookup

class UploadStep3Form(FlaskForm):
    vessel_type = SelectField('vessel_type', choices=[
        ('bottles',     "Bottles"),
        ('agar_plates', "Agar plates"),
        ('well_plates', "Well plates"),
        ('mini_react',  "Mini-bioreactors"),
    ], validators=[DataRequired()])

    bottle_count = IntegerField('bottle_count')
    plate_count  = IntegerField('plate_count')
    column_count = IntegerField('column_count')
    row_count    = IntegerField('row_count')

    timepoint_count = IntegerField('timepoint_count', validators=[DataRequired()])

    technique_type = SelectField('technique_type', choices=[
        ('od',        "Optical Density"),
        ('plates',    "Plate Counts"),
        ('plates_ps', "Plate Counts (per species)"),
        ('fc',        "Flow Cytometry"),
        ('fc_ps',     "Flow Cytometry (per species)"),
        ('rna',       "16S rRNA-seq"),
    ], validators=[DataRequired()])

    metabolites = SelectMultipleField('metabolites')

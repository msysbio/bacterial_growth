from flask_wtf import FlaskForm
from wtforms import SelectField, SelectMultipleField, StringField, IntegerField
from wtforms.validators import DataRequired, Optional


class UploadStep3Form(FlaskForm):
    vessel_type = SelectField('vessel_type', choices=[
        ('bottles',     "Bottles"),
        ('agar_plates', "Agar plates"),
        ('well_plates', "Well plates"),
        ('mini_react',  "mini bioreactors"),
    ])

    bottle_count = IntegerField('bottle_count')
    plate_count  = IntegerField('plate_count')
    column_count = IntegerField('column_count')
    row_count    = IntegerField('row_count')

    timepoint_count = IntegerField('timepoint_count')

    technique_type = SelectField('technique_type', choices=[
        ('od',        "Optical Density"),
        ('plates',    "Plate Counts"),
        ('plates_ps', "Plate Counts (per species)"),
        ('fc',        "Flow Cytometry"),
        ('fc_ps',     "Flow Cytometry (per species)"),
        ('rna',       "16S rRNA-seq"),
    ])

    technique_type = SelectMultipleField('metabolites')


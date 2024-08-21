from flask_wtf import FlaskForm
from wtforms import SelectField, StringField
from wtforms.validators import DataRequired

class SearchForm(FlaskForm):
    option = SelectField('option', choices=[
        'Project Name',
        'Project ID',
        'Study Name',
        'Study ID',
        'Microbial Strain',
        'NCBI ID',
        'Metabolites',
        'chEBI ID',
        'pH',
    ])
    value = StringField('value', validators=[DataRequired()])

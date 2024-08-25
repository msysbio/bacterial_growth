from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, FormField, FieldList
from wtforms.validators import DataRequired, Optional

class SearchFormClause(FlaskForm):
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
    logic_operator = SelectField('logic_operator', validators=[Optional()], choices=['AND', 'OR', 'NOT'])


class SearchForm(FlaskForm):
    clauses = FieldList(FormField(SearchFormClause), min_entries=1)

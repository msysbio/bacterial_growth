from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, FormField, FieldList
from wtforms.validators import Optional


class SearchFormClause(FlaskForm):
    option = SelectField('option', choices=[
        'Study Name',
        'Study ID',
        'Project Name',
        'Project ID',
        'Microbial Strain',
        'NCBI ID',
        'Metabolites',
        'chEBI ID',
        'pH',
    ])
    value = StringField('value', validators=[Optional()])
    logic_operator = SelectField('logic_operator', validators=[Optional()], choices=['AND', 'OR', 'NOT'])


class SearchForm(FlaskForm):
    clauses = FieldList(FormField(SearchFormClause), min_entries=1)

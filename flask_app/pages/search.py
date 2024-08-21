"""
Search for studies based on name, used metabolites, microbial strains, and
other criteria.
"""

from flask import render_template
import sqlalchemy as sql
import pandas as pd

from flask_app.db import get_connection
from flask_app.forms.search_form import SearchForm

from src.db_functions import dynamical_query

# TODO (2024-08-20) Put structured data into data frame, render properly
# -> Link to metabolite/member
# -> Metabolite page (pages/metabolite.py)
# -> Strain page (pages/strain.py)
#
# TODO (2024-08-20) Use SQLalchemy model instead


def search_index_page():
    form = SearchForm()

    if form.validate_on_submit():
        query = dynamical_query([{ 'option': form.option.data, 'value': form.value.data }])

        with get_connection() as conn:
            studyIds = [studyId for (studyId,) in conn.execute(sql.text(query))]

            if len(studyIds) == 0:
                message = "Couldn't find a study with these parameters."
                return render_template("pages/search/index.html", form=form, error=message)

            results = [get_general_info(studyId, conn) for studyId in studyIds]

            return render_template(
                "pages/search/index.html",
                form=form,
                results=results,
            )

    return render_template("pages/search/index.html", form=form)



def get_general_info(studyID, conn):
    query = f"SELECT * FROM Study WHERE studyId = '{studyID}';"
    df_general = pd.read_sql(query, conn)
    columns_to_exclude = ['studyId','projectUniqueID','studyUniqueID']
    df_general = df_general.drop(columns_to_exclude, axis=1)

    query = f"""
        SELECT CONCAT(memberName, ' (', NCBId, ')') AS transformed_output
        FROM Strains
        WHERE studyId = '{studyID}';
    """
    micro_strains = pd.read_sql(query, conn)
    df_general['memberName'] = ', '.join(micro_strains['transformed_output'])

    query = f"""
        SELECT DISTINCT technique
        FROM TechniquesPerExperiment
        WHERE studyId = '{studyID}';
    """
    techniques = pd.read_sql(query, conn)
    df_general['techniques'] = ', '.join(techniques['technique'])

    query = f"""
        SELECT DISTINCT CONCAT(metabo_name, ' (', cheb_id, ')') AS transformed_output
        FROM MetabolitePerExperiment
        WHERE studyId = '{studyID}';
    """
    metabolites = pd.read_sql(query, conn)
    df_general['metabolites'] = ', '.join(metabolites['transformed_output'])

    return df_general

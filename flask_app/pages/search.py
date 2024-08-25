"""
Search for studies based on name, used metabolites, microbial strains, and
other criteria.
"""

from flask import render_template
import sqlalchemy as sql

from flask_app.db import get_connection
from flask_app.forms.search_form import SearchForm, SearchFormClause
import flask_app.models.study_dfs as study_dfs


def search_index_page():
    form = SearchForm()

    template_clause = SearchFormClause()
    results = []

    if form.validate_on_submit():
        query = study_dfs.dynamical_query(form.data['clauses'])

        with get_connection() as conn:
            studyIds = [studyId for (studyId,) in conn.execute(sql.text(query))]

            if len(studyIds) == 0:
                message = "Couldn't find a study with these parameters."
                return render_template("pages/search/index.html", form=form, error=message)

            for studyId in studyIds:
                result = study_dfs.get_general_info(studyId, conn)

                result['experiments']               = study_dfs.get_experiments(studyId, conn)
                result['compartments']              = study_dfs.get_compartments(studyId, conn)
                result['communities']               = study_dfs.get_communities(studyId, conn)
                result['microbial_strains']         = study_dfs.get_microbial_strains(studyId, conn)
                result['biological_replicates']     = study_dfs.get_biological_replicates(studyId, conn)
                result['abundances']                = study_dfs.get_abundances(studyId, conn)
                result['fc_counts']                 = study_dfs.get_fc_counts(studyId, conn)
                result['metabolites_per_replicate'] = study_dfs.get_metabolites_per_replicate(studyId, conn)

                results.append(result)

    return render_template(
        "pages/search/index.html",
        form=form,
        template_clause=template_clause,
        results=results
    )

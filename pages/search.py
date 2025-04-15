"""
Search for studies based on name, used metabolites, microbial strains, and
other criteria.
"""

from flask import (
    g,
    render_template,
)
import sqlalchemy as sql

from db import get_connection
from forms.search_form import SearchForm, SearchFormClause
import models.study_dfs as study_dfs
from models import (
    Study,
    StudyUser,
)


def search_index_page():
    form = SearchForm()

    template_clause = SearchFormClause()
    results = []

    if form.validate_on_submit():
        query = study_dfs.dynamical_query(form.data['clauses'])

        studyIds = [studyId for (studyId,) in g.db_conn.execute(sql.text(query))]

        if len(studyIds) == 0:
            message = "Couldn't find a study with these parameters."
            return render_template("pages/search/index.html", form=form, error=message, template_clause=template_clause)
    else:
        # TODO (2025-04-15) Extract, test with multiple users
        studyIds = g.db_session.scalars(
            sql.select(Study.studyId)
            .join(StudyUser)
            .where(sql.or_(
                Study.isPublished,
                StudyUser.userUniqueID == g.current_user.uuid
            ))
            .order_by(Study.updatedAt.desc())
            .limit(5)
        ).all()

    for studyId in studyIds:
        result = study_dfs.get_general_info(studyId, g.db_conn)

        result['experiments']               = study_dfs.get_experiments(studyId, g.db_conn)
        result['compartments']              = study_dfs.get_compartments(studyId, g.db_conn)
        result['communities']               = study_dfs.get_communities(studyId, g.db_conn)
        result['microbial_strains']         = study_dfs.get_microbial_strains(studyId, g.db_conn)
        result['biological_replicates']     = study_dfs.get_biological_replicates(studyId, g.db_conn)
        result['abundances']                = study_dfs.get_abundances(studyId, g.db_conn)
        result['fc_counts']                 = study_dfs.get_fc_counts(studyId, g.db_conn)
        result['metabolites_per_replicate'] = study_dfs.get_metabolites_per_replicate(studyId, g.db_conn)

        results.append(result)

    return render_template(
        "pages/search/index.html",
        form=form,
        template_clause=template_clause,
        results=results
    )

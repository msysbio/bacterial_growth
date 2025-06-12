"""
Search for studies based on name, used metabolites, microbial strains, and
other criteria.
"""

from flask import (
    g,
    render_template,
    request,
)
import sqlalchemy as sql

from app.view.forms.search_form import SearchForm, SearchFormClause
import app.model.lib.study_dfs as study_dfs
from app.model.orm import (
    Study,
    StudyUser,
)


def search_index_page():
    form = SearchForm(request.args)

    template_clause = SearchFormClause()
    results = []

    if form.data['clauses'] and form.data['clauses'][0]['value']:
        if not form.data['clauses'][0]['option']:
            form.data

        query, values = study_dfs.dynamical_query(form.data['clauses'])
        value_dict = {f"value_{i}": v for i, v in enumerate(values)}
        studyIds = [
            studyId for (studyId,)
            in g.db_conn.execute(sql.text(query), value_dict)
        ]

        if len(studyIds) == 0:
            message = "Couldn't find a study with these parameters."
            return render_template(
                "pages/search/index.html",
                form=form,
                error=message,
                template_clause=template_clause,
            )
    else:
        if g.current_user:
            publish_clause = sql.or_(
                Study.isPublished,
                StudyUser.userUniqueID == g.current_user.uuid
            )
        else:
            publish_clause = Study.isPublished

        # TODO (2025-04-15) Extract, test with multiple users
        studyIds = g.db_session.scalars(
            sql.select(Study.studyId)
            .join(StudyUser, isouter=True)
            .where(publish_clause)
            .order_by(Study.updatedAt.desc())
            .limit(5)
        ).all()

    if studyIds:
        query = sql.select(Study).where(Study.publicId.in_(studyIds))
        results = g.db_session.scalars(query)

    return render_template(
        "pages/search/index.html",
        form=form,
        template_clause=template_clause,
        results=results
    )

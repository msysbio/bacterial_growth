from flask import (
    g,
    render_template,
)
import sqlalchemy as sql

from app.model.orm import Project


def project_show_page(projectId):
    project = g.db_session.scalars(
        sql.select(Project)
        .where(Project.projectId == projectId)
        .limit(1)
    ).one()

    return render_template("pages/projects/show.html", project=project)

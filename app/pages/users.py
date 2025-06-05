import os

from flask import (
    g,
    render_template,
    redirect,
    request,
    session,
    flash,
    current_app,
    url_for,
)
import sqlalchemy as sql
import requests

from app.model.orm import (
    Project,
    ProjectUser,
    Study,
    StudyUser,
    Strain,
)
from app.model.lib import orcid


def user_show_page():
    projects = []
    studies = []
    custom_strains = []

    if g.current_user:
        projects = g.db_session.scalars(
            sql.select(Project)
            .join(ProjectUser)
            .where(ProjectUser.userUniqueID == g.current_user.uuid)
            .order_by(Project.projectId.asc())
        ).all()

        studies = g.db_session.scalars(
            sql.select(Study)
            .join(StudyUser)
            .where(StudyUser.userUniqueID == g.current_user.uuid)
            .order_by(Study.studyId.asc())
        ).all()

        custom_strains = g.db_session.scalars(
            sql.select(Strain)
            .where(
                Strain.userUniqueID == g.current_user.uuid,
                Strain.defined.is_(False),
            )
            .order_by(Strain.name.desc())
        ).all()

    return render_template(
        'pages/users/show.html',
        projects=projects,
        studies=studies,
        custom_strains=custom_strains,
    )


def user_login_page():
    if 'code' in request.args:
        return _user_login_submit(request.args['code'])
    else:
        return _user_login_show()


def user_claim_project_action():
    project_uuid = request.form['uuid'].strip()
    user_uuid    = g.current_user.uuid

    project = g.db_session.get(Project, project_uuid)
    if not project:
        flash(f"A project with this UUID couldn't be found: {repr(project_uuid)}", 'error')
        return redirect(request.referrer)

    # Check for link existence:
    project_user = g.db_session.scalars(
        sql.select(ProjectUser)
        .where(
            ProjectUser.userUniqueID == user_uuid,
            ProjectUser.projectUniqueID == project_uuid,
        )
        .limit(1)
    ).one_or_none()

    if project_user:
        flash(f"You already have access to this project: [{project.publicId}] {project.name}", "error")
    else:
        # Create link:
        g.db_session.add(ProjectUser(userUniqueID=user_uuid, projectUniqueID=project_uuid))
        g.db_session.commit()

    return redirect(request.referrer)


def user_claim_study_action():
    study_uuid = request.form['uuid'].strip()
    user_uuid  = g.current_user.uuid

    study = g.db_session.get(Study, study_uuid)
    if not study:
        flash(f"A study with this UUID couldn't be found: {repr(study_uuid)}", 'error')
        return redirect(request.referrer)

    # Check for link existence:
    study_user = g.db_session.scalars(
        sql.select(StudyUser)
        .where(
            StudyUser.userUniqueID == user_uuid,
            StudyUser.studyUniqueID == study_uuid,
        )
        .limit(1)
    ).one_or_none()

    if study_user:
        flash(f"You already have access to this study: [{study.publicId}] {study.name}", "error")
    else:
        # Create link:
        g.db_session.add(StudyUser(userUniqueID=user_uuid, studyUniqueID=study_uuid))
        g.db_session.commit()

    return redirect(request.referrer)


def _user_login_show():
    app_env = os.getenv('APP_ENV', 'development')

    orcid_url = orcid.get_login_url(request.host)

    return render_template(
        "pages/users/login.html",
        orcid_url=orcid_url,
    )


def _user_login_submit(orcid_code):
    orcid_secret = current_app.config["ORCID_SECRET"]
    user_data = orcid.authenticate_user(orcid_code, orcid_secret, request.host)

    # print(user_data)
    # {
    #     'access_token': '41fafcd6-30aa-40da-959c-4267fc9eb211',
    #     'token_type': 'bearer',
    #     'refresh_token': '3c967090-e009-4e57-868a-533459a21de4',
    #     'expires_in': 631138518,
    #     'scope': 'openid',
    #     'name': 'Andrey Radev',
    #     'orcid': '0009-0009-0846-2326',
    #     'id_token': '...',
    # }

    return redirect(url_for('user_show_page'))

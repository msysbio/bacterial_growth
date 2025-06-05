import os
from datetime import datetime, UTC

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
from werkzeug.exceptions import NotFound

from app.model.orm import (
    Project,
    ProjectUser,
    Strain,
    Study,
    StudyUser,
    User,
)
from app.model.lib import orcid


def user_show_page():
    if not g.current_user:
        return redirect(url_for('user_login_page'))

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
        custom_strains=custom_strains,
    )


def user_login_page():
    if 'code' in request.args:
        return _user_login_submit(request.args['code'])
    else:
        return _user_login_show()


def user_backdoor_page():
    app_env = os.getenv('APP_ENV', 'development')
    if app_env not in ('development', 'test'):
        raise NotFound()

    if request.method == 'POST':
        session['user_uuid'] = request.form['user_uuid'].strip()
        return redirect(url_for('static_home_page'))
    else:
        return render_template("pages/users/backdoor.html")


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


def user_logout_action():
    del session['user_uuid']

    return redirect(url_for('static_home_page'))


def _user_login_show():
    app_env         = os.getenv('APP_ENV', 'development')
    orcid_client_id = current_app.config["ORCID_CLIENT_ID"]

    orcid_url = orcid.get_login_url(orcid_client_id, request.host)

    return render_template(
        "pages/users/login.html",
        orcid_url=orcid_url,
    )


def _user_login_submit(orcid_code):
    orcid_client_id = current_app.config["ORCID_CLIENT_ID"]
    orcid_secret    = current_app.config["ORCID_SECRET"]

    user_data = orcid.authenticate_user(orcid_code, orcid_client_id, orcid_secret, request.host)

    user = g.db_session.scalars(
        sql.select(User)
        .where(User.orcidId == user_data['orcid'])
        .limit(1)
    ).one_or_none()

    if not user:
        user = User(
            uuid=session['user_uuid'],
            orcidId=user_data['orcid'],
        )

    user.name        = user_data['name']
    user.orcidToken  = user_data['access_token']
    user.lastLoginAt = datetime.now(UTC)

    g.db_session.add(user)
    g.db_session.commit()

    session['user_uuid'] = user.uuid

    return redirect(url_for('user_show_page'))

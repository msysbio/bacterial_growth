from flask import (
    g,
    render_template,
    redirect,
    request,
    session,
    flash,
)
import sqlalchemy as sql

from app.model.orm import (
    Project,
    ProjectUser,
    Study,
    StudyUser,
    Strain,
)


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


def user_login_action():
    session['user_uuid'] = request.form['user_uuid'].strip()

    return redirect(request.referrer)


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

from db import get_session

import sqlalchemy as sql

from app.model.orm import (
    Project,
    Study,
    ProjectUser,
    StudyUser,
)

user_uuid = 'b5d6e7b6-b39c-4ffe-be22-84d58b6ee964'

with get_session() as db_session:
    for project_uuid in db_session.scalars(sql.select(Project.projectUniqueID)):
        project_user = db_session.scalars(
            sql.select(ProjectUser)
            .where(
                ProjectUser.projectUniqueID == project_uuid,
                ProjectUser.userUniqueID == user_uuid,
            )
        ).one_or_none()

        if project_user:
            print(f"Existing project user: {project_user.id}")
        else:
            project_user = ProjectUser(
                projectUniqueID=project_uuid,
                userUniqueID=user_uuid,
            )

            db_session.add(project_user)
            print(f"New project user for project UUID: {project_uuid}")

    for study_uuid in db_session.scalars(sql.select(Study.studyUniqueID)):
        study_user = db_session.scalars(
            sql.select(StudyUser)
            .where(
                StudyUser.studyUniqueID == study_uuid,
                StudyUser.userUniqueID == user_uuid,
            )
        ).one_or_none()

        if study_user:
            print(f"Existing study user: {study_user.id}")
        else:
            study_user = StudyUser(
                studyUniqueID=study_uuid,
                userUniqueID=user_uuid,
            )

            db_session.add(study_user)
            print(f"New study user for study UUID: {study_uuid}")

    db_session.commit()

from uuid import uuid4
from datetime import datetime, UTC

import sqlalchemy as sql
import simplejson as json

from app.model.orm import (
    ExcelFile,
    Project,
    Study,
    Submission,
)
from app.view.forms.submission_form import SubmissionForm
from app.model.lib.submission_process import persist_submission_to_database


def bootstrap_study(db_session, study_key, user_uuid):
    submission = Submission(
        studyUniqueID=str(uuid4()),
        projectUniqueID=str(uuid4()),
        userUniqueID=user_uuid,
    )

    json_path = f"scripts/bootstrap/submission_data/{study_key}.json"
    with open(json_path, 'r') as f:
        submission.studyDesign = json.load(f, use_decimal=True)

    project_name = submission.studyDesign['project']['name']
    study_name   = submission.studyDesign['study']['name']

    existing_project = db_session.scalars(
        sql.select(Project)
        .where(Project.name == project_name)
        .limit(1)
    ).one_or_none()

    if existing_project:
        print(f"> Skipping project {project_name}, already exists ({existing_project.publicId})")
        return

    data_excel_path = f"scripts/bootstrap/measurement_data/{study_key}.xlsx"
    with open(data_excel_path, 'rb') as f:
        excel_bytes = f.read()

    submission.dataFile = ExcelFile(
        filename=data_excel_path,
        content=excel_bytes,
        size=len(excel_bytes),
    )
    db_session.add(submission)
    db_session.commit()

    submission_form = SubmissionForm(
        submission_id=submission.id,
        db_session=db_session,
        user_uuid=user_uuid,
    )

    errors = persist_submission_to_database(submission_form)
    if errors:
        raise ValueError(f"Errors: {repr(errors)}")
    db_session.commit()

    study = db_session.scalars(
        sql.select(Study)
        .where(Study.name == study_name)
        .limit(1)
    ).one()

    study.publishedAt = datetime.now(UTC)
    db_session.add(study)
    db_session.commit()

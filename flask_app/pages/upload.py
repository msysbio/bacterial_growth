from uuid import uuid4

from flask import render_template, session, request, redirect, url_for

from flask_app.db import get_connection
from flask_app.models.submission import Submission


def upload_index_page(step=None):
    submission = Submission(session.get('submission', {}), current_step=step)

    return render_template(
        "pages/upload/index.html",
        submission=submission
    )

# TODO (2024-09-19) Validate project uuid in database: Render step 1 with error
#
def submit_step_1_upload():
    with get_connection() as conn:
        submission = Submission(session.get('submission', {}), current_step=1)
        submission.type = request.form['submission_type']

        if submission.type == 'new_project':
            if submission.project_uuid is None:
                submission.project_uuid = uuid4()
            if submission.study_uuid is None:
                submission.study_uuid = uuid4()

            submission.project = {
                'name':        request.form['project_name'],
                'description': request.form['project_description'],
            }
        elif submission.type == 'new_study':
            submission.project_uuid = request.form['project_uuid']
            if submission.study_uuid is None:
                submission.study_uuid = uuid4()

            submission.project = {
                'name':        f"[TODO] Name of project {submission.project_uuid}",
                'description': f"[TODO] Description of project {submission.project_uuid}",
            }
        elif submission.type == 'update_study':
            submission.project_uuid = request.form['project_uuid']
            submission.study_uuid   = request.form['study_uuid']

            submission.project = {
                'name':        f"[TODO] Name of project {submission.project_uuid}",
                'description': f"[TODO] Description of project {submission.project_uuid}",
            }
        else:
            raise KeyError("Unknown submission type: {}".format(submission_type))

        session['submission'] = submission._asdict()

        return redirect(url_for('upload_index_page', step=2))

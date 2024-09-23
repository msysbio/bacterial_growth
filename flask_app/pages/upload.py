from uuid import uuid4

from flask import render_template, session, request, redirect, url_for

from flask_app.db import get_connection
from flask_app.models.submission import Submission
from flask_app.forms.upload_step2_form import UploadStep2Form


def upload_index_page(step=None):
    with get_connection() as conn:
        submission = Submission(session.get('submission', {}), current_step=step, db_conn=conn)

        return render_template(
            "pages/upload/index.html",
            submission=submission,
        )


def submit_step_1_upload():
    with get_connection() as conn:
        submission = Submission(session.get('submission', {}), current_step=1, db_conn=conn)
        submission.update_project(request.form)

        if submission.project:
            session['submission'] = submission._asdict()
            return redirect(url_for('upload_index_page', step=2))
        else:
            # No project data found, show error:

            return render_template(
                "pages/upload/index.html",
                submission=submission,
                error="No project found with this UUID"
            )

def submit_step_2_upload():
    with get_connection() as conn:
        submission = Submission(session.get('submission', {}), current_step=2, db_conn=conn)
        form = UploadStep2Form(request.form)

        # TODO (2024-09-22) Validate form

        submission.update_strains(form.data)
        session['submission'] = submission._asdict()

        return redirect(url_for('upload_index_page', step=3))

def submit_step_3_upload():
    with get_connection() as conn:
        submission = Submission(session.get('submission', {}), current_step=3, db_conn=conn)
        form = UploadStep3Form(request.form)

        submission.update_study_design(form.data)
        session['submission'] = submission._asdict()

        return redirect(url_for('upload_index_page', step=4))

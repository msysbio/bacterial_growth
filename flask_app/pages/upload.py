from uuid import uuid4

from flask import render_template, session, request, redirect, url_for

from flask_app.db import get_connection
from flask_app.models.submission import Submission
from flask_app.forms.upload_step2_form import UploadStep2Form


def upload_index_page(step=None):
    with get_connection() as conn:
        submission = Submission(session.get('submission', {}), current_step=step, db_conn=conn)
        print(submission._asdict())

        step2_form = UploadStep2Form(request.form, obj=submission) if step == 2 else None

        return render_template(
            "pages/upload/index.html",
            submission=submission,
            step2_form=step2_form
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
        submission = Submission(session.get('submission', {}), current_step=1, db_conn=conn)
        form = UploadStep2Form(request.form)

        # TODO (2024-09-22) Validate form

        submission.update_strains(form)
        session['submission'] = submission._asdict()

        return redirect(url_for('upload_index_page', step=3))

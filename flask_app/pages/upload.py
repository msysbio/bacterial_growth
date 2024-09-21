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


def submit_step_1_upload():
    with get_connection() as conn:
        submission = Submission(session.get('submission', {}), current_step=1)
        submission.update_project(request.form, conn)

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

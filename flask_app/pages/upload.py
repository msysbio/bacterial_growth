from uuid import uuid4

from flask import render_template, session, request, redirect, url_for

from flask_app.db import get_connection
from flask_app.models.submission import Submission
from flask_app.forms.upload_step2_form import UploadStep2Form
from flask_app.forms.upload_step3_form import UploadStep3Form


def upload_step1_page():
    with get_connection() as conn:
        submission = Submission(session.get('submission', {}), current_step=1, db_conn=conn)
        error = None

        if request.form:
            submission.update_project(request.form)

            if submission.project:
                session['submission'] = submission._asdict()
                return redirect(url_for('upload_step2_page'))
            else:
                error = "No project found with this UUID"

        return render_template(
            "pages/upload/index.html",
            submission=submission,
            error=error
        )


def upload_step2_page():
    with get_connection() as conn:
        submission = Submission(session.get('submission', {}), current_step=2, db_conn=conn)
        form = UploadStep2Form(request.form)

        if form.validate_on_submit():
            submission.update_strains(form.data)
            session['submission'] = submission._asdict()

            return redirect(url_for('upload_step3_page'))

        return render_template(
            "pages/upload/index.html",
            submission=submission,
        )


def upload_step3_page():
    with get_connection() as conn:
        submission = Submission(session.get('submission', {}), current_step=3, db_conn=conn)
        form = UploadStep3Form(request.form)

        if form.validate_on_submit():
            submission.update_study_design(form.data)
            session['submission'] = submission._asdict()

            return redirect(url_for('upload_step3_page'))

        return render_template(
            "pages/upload/index.html",
            submission=submission,
        )


def upload_step4_page():
    with get_connection() as conn:
        submission = Submission(session.get('submission', {}), current_step=4, db_conn=conn)

        return render_template(
            "pages/upload/index.html",
            submission=submission,
        )

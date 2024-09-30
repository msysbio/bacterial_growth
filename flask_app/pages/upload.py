import io

from flask import render_template, session, request, redirect, url_for, send_file

from flask_app.db import get_connection
from flask_app.models.submission import Submission
import flask_app.models.data_spreadsheet as data_spreadsheet
from flask_app.forms.upload_step2_form import UploadStep2Form
from flask_app.forms.upload_step3_form import UploadStep3Form


def upload_status_page():
    with get_connection() as conn:
        submission = Submission(session.get('submission', {}), step=0, db_conn=conn)

        return render_template(
            "pages/upload/index.html",
            submission=submission,
        )


def upload_step1_page():
    with get_connection() as conn:
        submission = Submission(session.get('submission', {}), step=1, db_conn=conn)
        error = None

        if request.method == 'POST':
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
        submission = Submission(session.get('submission', {}), step=2, db_conn=conn)
        form = UploadStep2Form(request.form)

        if request.method == 'POST':
            submission.update_strains(form.data)
            session['submission'] = submission._asdict()

            return redirect(url_for('upload_step3_page'))

        return render_template(
            "pages/upload/index.html",
            submission=submission,
        )


def upload_step3_page():
    with get_connection() as conn:
        submission = Submission(session.get('submission', {}), step=3, db_conn=conn)
        form = UploadStep3Form(request.form, obj=submission)

        if request.method == 'POST':
            submission.update_study_design(form.data)
            session['submission'] = submission._asdict()

            metabolite_names = [name for (id, name) in submission.fetch_metabolites()]
            taxa_names       = [name for (id, name) in submission.fetch_strains()]

            spreadsheet = data_spreadsheet.create_excel(
                submission.technique_type,
                metabolite_names,
                submission.vessel_type,
                submission.vessel_count,
                submission.column_count,
                submission.row_count,
                submission.timepoint_count,
                taxa_names,
            )

            return send_file(
                io.BytesIO(spreadsheet),
                as_attachment=True,
                download_name=f"template_data.xlsx",
            )

            return redirect(url_for('upload_step3_page'))

        return render_template(
            "pages/upload/index.html",
            submission=submission,
            form=form
        )


def upload_step4_page():
    with get_connection() as conn:
        submission = Submission(session.get('submission', {}), step=4, db_conn=conn)

        return render_template(
            "pages/upload/index.html",
            submission=submission,
        )

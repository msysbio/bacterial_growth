import io
import os
import tempfile

from flask import (
    g,
    render_template,
    session,
    request,
    redirect,
    url_for,
    send_file,
)
import humanize
import pandas as pd
import sqlalchemy as sql

from models import (
    Measurement,
    Submission,
    ExcelFile,
    Project,
    ProjectUser,
    Study,
    StudyUser,
)
from forms.submission_form import SubmissionForm

import legacy.study_spreadsheet as study_spreadsheet
import legacy.data_spreadsheet as data_spreadsheet
from legacy.upload_validation import validate_upload
from legacy.populate_db import save_measurements_to_database
from legacy.chart_data import save_chart_data_to_files

from forms.upload_step2_form import UploadStep2Form
from forms.upload_step3_form import UploadStep3Form


def upload_status_page():
    submission_form = _init_submission_form(step=0)

    if g.current_user.uuid:
        user_submissions = g.db_session.scalars(
            sql.select(Submission)
            .where(Submission.userUniqueID == g.current_user.uuid)
            .order_by(Submission.updatedAt)
        ).all()
    else:
        user_submissions = None

    return render_template(
        "pages/upload/index.html",
        submission_form=submission_form,
        submission=submission_form.submission,
        user_submissions=user_submissions,
    )


def upload_step1_page():
    submission_form = _init_submission_form(step=1)

    if request.method == 'POST':
        submission_form.update_project(request.form)

        if len(submission_form.errors) == 0:
            session['submission_id'] = submission_form.save()
            return redirect(url_for('upload_step2_page'))

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
    else:
        projects = []
        studies = []

    return render_template(
        "pages/upload/index.html",
        submission_form=submission_form,
        submission=submission_form.submission,
        projects=projects,
        studies=studies,
    )


def upload_step2_page():
    submission_form = _init_submission_form(step=2)
    form = UploadStep2Form(request.form)

    if request.method == 'POST':
        submission_form.update_strains(form.data)
        session['submission_id'] = submission_form.save()

        return redirect(url_for('upload_step3_page'))

    return render_template(
        "pages/upload/index.html",
        submission_form=submission_form,
        submission=submission_form.submission,
    )


def upload_step3_page():
    submission_form = _init_submission_form(step=3)
    submission = submission_form.submission

    if request.method == 'POST':
        form = UploadStep3Form(request.form)

        submission_form.update_study_design(form.data)
        session['submission_id'] = submission_form.save()

        return redirect(url_for('upload_step4_page'))

    else:
        upload_form = UploadStep3Form(data=submission.studyDesign)

        return render_template(
            "pages/upload/index.html",
            submission_form=submission_form,
            submission=submission_form.submission,
            upload_form=upload_form
        )


def download_study_template_xlsx():
    submission_form = _init_submission_form(step=3)
    submission = submission_form.submission

    taxa_ids   = submission.studyDesign['strains']
    taxa_names = [t.tax_names for t in submission_form.fetch_taxa()]

    new_strains = [
        {
            'case_number':     index,
            'name':            strain['name'],
            'description':     strain['description'],
            'parent_taxon_id': strain['species'],
        }
        for (index, strain)
        in enumerate(submission_form.fetch_new_strains())
    ]

    spreadsheet = study_spreadsheet.create_excel(
        taxa_names,
        taxa_ids,
        new_strains,
        submission.projectUniqueID,
        submission.studyUniqueID,
    )

    return send_file(
        io.BytesIO(spreadsheet),
        as_attachment=True,
        download_name="template_study.xlsx",
    )


def download_data_template_xlsx():
    submission_form = _init_submission_form(step=3)
    submission = submission_form.submission

    metabolite_names = [m.metabo_name for m in submission_form.fetch_all_metabolites()]
    strain_names = [t.tax_names for t in submission_form.fetch_taxa()]
    strain_names += [s['name'] for s in submission_form.fetch_new_strains()]

    spreadsheet = data_spreadsheet.create_excel(
        submission,
        metabolite_names,
        strain_names,
    )

    return send_file(
        io.BytesIO(spreadsheet),
        as_attachment=True,
        download_name="template_data.xlsx",
    )


def upload_step4_page():
    submission_form = _init_submission_form(step=4)
    submission = submission_form.submission
    errors = []

    if request.method == 'POST':
        if request.files['study-template']:
            submission.studyFile = ExcelFile.from_upload(request.files['study-template'])
        if request.files['data-template']:
            submission.dataFile  = ExcelFile.from_upload(request.files['data-template'])

        submission_form.save()

        with tempfile.TemporaryDirectory() as yml_dir:
            errors = validate_upload(yml_dir, submission)

            if len(errors) == 0:
                # TODO (2025-04-03) instead of returning all that, return updated submission_form
                (study_id, errors, errors_logic, studyUniqueID, projectUniqueID, project_id) = \
                    save_measurements_to_database(g.db_session, yml_dir, submission_form, submission.dataFile.content)
                g.db_session.commit()

                if len(errors) == 0:
                    study = g.db_session.get(Study, studyUniqueID)
                    _save_chart_data_to_database(g.db_session, study, submission)
                    submission_form.save()

                    return redirect(url_for('upload_step5_page'))

    return render_template(
        "pages/upload/index.html",
        submission_form=submission_form,
        submission=submission_form.submission,
        errors=errors,
    )


def upload_spreadsheet_preview_fragment():
    excel_file = ExcelFile.from_upload(request.files['file'])

    return render_template(
        "pages/upload/step4/spreadsheet_preview.html",
        excel_file=excel_file,
    )


def upload_step5_page():
    submission_form = _init_submission_form(step=5)

    return render_template(
        "pages/upload/index.html",
        submission_form=submission_form,
        submission=submission_form.submission,
    )


def _init_submission_form(step):
    return SubmissionForm(
        session.get('submission_id', None),
        step=step,
        db_session=g.db_session,
        user_uuid=g.current_user.uuid,
    )


def _save_chart_data_to_database(db_session, study, submission):
    data_xls = submission.dataFile.content
    sheets = pd.read_excel(io.BytesIO(data_xls))

    if 'Growth data per community' in sheets:
        df = sheets['Growth data per community']
        Measurement.insert_from_bioreplicates_csv(db_session, study, df.to_csv(index=False))

    if 'Growth data per strain' in sheets:
        df = sheets['Growth data per strain']
        Measurement.insert_from_strain_csv(db_session, study, df.to_csv(index=False))

    if 'Growth data per metabolite' in sheets:
        df = sheets['Growth data per metabolite']
        Measurement.insert_from_metabolites_csv(db_session, study, df.to_csv(index=False))

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
    submission_form = SubmissionForm(
        session.get('submission_id', None),
        step=0,
        db_session=g.db_session,
        user_uuid=g.current_user.uuid,
    )

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


def new_submission_action():
    if 'submission_id' in session:
        del session['submission_id']

    return redirect(url_for('upload_step1_page'))


def edit_submission_action(id):
    session['submission_id'] = id

    return redirect(url_for('upload_status_page'))


def delete_submission_action(id):
    if 'submission_id' in session:
        del session['submission_id']

    g.db_session.execute(sql.delete(Submission).where(Submission.id == id))
    g.db_session.commit()

    return redirect(url_for('upload_status_page'))


def upload_step1_page():
    submission_form = SubmissionForm(
        session.get('submission_id', None),
        step=1,
        db_session=g.db_session,
        user_uuid=g.current_user.uuid,
    )
    error = None

    if request.method == 'POST':
        submission_form.update_project(request.form)
        session['submission_id'] = submission_form.save()

        return redirect(url_for('upload_step2_page'))

    return render_template(
        "pages/upload/index.html",
        submission_form=submission_form,
        submission=submission_form.submission,
        error=error
    )


def upload_step2_page():
    submission_form = SubmissionForm(
        session.get('submission_id', None),
        step=2,
        db_session=g.db_session,
        user_uuid=g.current_user.uuid,
    )
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
    submission_form = SubmissionForm(
        session.get('submission_id', None),
        step=3,
        db_session=g.db_session,
        user_uuid=g.current_user.uuid,
    )
    submission = submission_form.submission

    if request.method == 'POST':
        form = UploadStep3Form(request.form)
        submission_form.update_study_design(form.data)
        session['submission_id'] = submission_form.save()

        metabolite_names = [m.metabo_name for m in submission_form.fetch_metabolites()]
        taxa_names       = [t.tax_names for t in submission_form.fetch_taxa()]

        spreadsheet = data_spreadsheet.create_excel(
            submission.studyDesign['technique_types'],
            metabolite_names,
            submission.studyDesign['vessel_type'],
            submission.studyDesign['vessel_count'],
            submission.studyDesign['column_count'],
            submission.studyDesign['row_count'],
            submission.studyDesign['timepoint_count'],
            taxa_names,
        )

        return send_file(
            io.BytesIO(spreadsheet),
            as_attachment=True,
            download_name="template_data.xlsx",
        )
    else:
        upload_form = UploadStep3Form(data=submission.studyDesign)

        return render_template(
            "pages/upload/index.html",
            submission_form=submission_form,
            submission=submission_form.submission,
            upload_form=upload_form
        )


def upload_study_template_xlsx():
    submission_form = SubmissionForm(
        session.get('submission_id', None),
        step=3,
        db_session=g.db_session,
        user_uuid=g.current_user.uuid,
    )
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


def upload_step4_page():
    submission_form = SubmissionForm(
        session.get('submission_id', None),
        step=4,
        db_session=g.db_session,
        user_uuid=g.current_user.uuid,
    )
    submission = submission_form.submission
    errors = []

    if request.method == 'POST':
        with tempfile.TemporaryDirectory() as yml_dir:
            if request.files['study-template']:
                submission.studyFile = ExcelFile.from_upload(request.files['study-template'])
            if request.files['data-template']:
                submission.dataFile  = ExcelFile.from_upload(request.files['data-template'])

            # TODO (2025-01-30) Check for project name and study name uniqueness

            errors = validate_upload(yml_dir, submission.studyFile.content, submission.dataFile.content)

            if len(errors) == 0:
                (study_id, errors, errors_logic, studyUniqueID, projectUniqueID, project_id) = \
                    save_measurements_to_database(g.db_session, yml_dir, submission_form, submission.dataFile.content)

                if len(errors) == 0:
                    # TODO (2025-01-30) Message that data was successfully
                    # stored, reset submission. (Later, store submission as
                    # draft?)
                    #
                    # st.success(f"""Thank you! your study has been successfully uploaded into our database,
                    #         **Private Study ID**: {studyUniqueID} and **Study ID**: {study_id},
                    #         **Private Project Id**: {projectUniqueID} and **Project ID**: {project_id}""")

                    save_chart_data_to_files(study_id, submission.dataFile.content)
                    _save_chart_data_to_database(g.db_session, study_id, submission.dataFile.content)
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
    submission_form = SubmissionForm(
        session.get('submission_id', None),
        step=5,
        db_session=g.db_session,
        user_uuid=g.current_user.uuid,
    )

    return render_template(
        "pages/upload/index.html",
        submission_form=submission_form,
        submission=submission_form.submission,
    )


def _save_chart_data_to_database(db_session, study_id, data_xls):
    df_excel_growth = pd.read_excel(data_xls, sheet_name='Growth_Data_and_Metabolites')
    # Drop columns with NaN values
    df_excel_growth = df_excel_growth.dropna(axis=1, how='all')
    # Drop rows where all values are NaN
    df_excel_growth = df_excel_growth.dropna(axis=0, how='all')

    if not df_excel_growth.empty:
        Measurement.insert_from_growth_csv(db_session, study_id, df_excel_growth.to_csv(index=False))

    df_excel_reads = pd.read_excel(data_xls, sheet_name='growth_per_species')
    # Drop columns with NaN values
    df_excel_reads = df_excel_reads.dropna(axis=1, how='all')
    subset_columns = df_excel_reads.columns.drop('Position')
    # Drop rows where all values are NaN
    df_excel_reads = df_excel_reads.dropna(subset=subset_columns, how='all')

    if not df_excel_reads.empty:
        Measurement.insert_from_reads_csv(db_session, study_id, df_excel_reads.to_csv(index=False))

import io
import os
import tempfile

from flask import render_template, session, request, redirect, url_for, send_file
import humanize
import pandas as pd

from db import (
    get_connection,
    get_transaction,
    get_session,
)
from models import Measurement
from forms.submission_form import SubmissionForm
import models.spreadsheet_preview as spreasheet_preview

import legacy.study_spreadsheet as study_spreadsheet
import legacy.data_spreadsheet as data_spreadsheet
from legacy.upload_validation import validate_upload
from legacy.populate_db import save_submission_to_database
from legacy.chart_data import save_chart_data_to_files

from forms.upload_step2_form import UploadStep2Form
from forms.upload_step3_form import UploadStep3Form


def upload_status_page():
    with get_connection() as conn:
        submission_form = SubmissionForm(session.get('submission', {}), step=0, db_conn=conn)

        return render_template(
            "pages/upload/index.html",
            submission_form=submission_form,
        )


def upload_step1_page():
    with get_connection() as conn:
        submission_form = SubmissionForm(session.get('submission', {}), step=1, db_conn=conn)
        error = None

        if request.method == 'POST':
            submission_form.update_project(request.form)

            if submission_form.project:
                session['submission'] = submission_form._asdict()
                return redirect(url_for('upload_step2_page'))
            else:
                error = "No project found with this UUID"

        return render_template(
            "pages/upload/index.html",
            submission_form=submission_form,
            error=error
        )


def upload_step2_page():
    with get_connection() as conn:
        submission_form = SubmissionForm(session.get('submission', {}), step=2, db_conn=conn)
        form = UploadStep2Form(request.form)

        if request.method == 'POST':
            submission_form.update_strains(form.data)
            session['submission_form'] = submission_form._asdict()

            return redirect(url_for('upload_step3_page'))

        return render_template(
            "pages/upload/index.html",
            submission_form=submission_form,
        )


def upload_step3_page():
    with get_connection() as conn:
        submission_form = SubmissionForm(session.get('submission', {}), step=3, db_conn=conn)

        if request.method == 'POST':
            form = UploadStep3Form(request.form)
            submission_form.update_study_design(form.data)
            session['submission'] = submission_form._asdict()

            metabolite_names = [name for (id, name) in submission_form.fetch_metabolites()]
            taxa_names       = [name for (id, name) in submission_form.fetch_strains()]

            spreadsheet = data_spreadsheet.create_excel(
                submission_form.technique_types,
                metabolite_names,
                submission_form.vessel_type,
                submission_form.vessel_count,
                submission_form.column_count,
                submission_form.row_count,
                submission_form.timepoint_count,
                taxa_names,
            )

            return send_file(
                io.BytesIO(spreadsheet),
                as_attachment=True,
                download_name="template_data.xlsx",
            )
        else:
            upload_form = UploadStep3Form(obj=submission_form)

            return render_template(
                "pages/upload/index.html",
                submission_form=submission_form,
                upload_form=upload_form
            )


def upload_study_template_xlsx():
    with get_connection() as conn:
        submission_form = SubmissionForm(session.get('submission', {}), step=3, db_conn=conn)

        taxa_ids   = submission_form.strains
        taxa_names = [name for (id, name) in submission_form.fetch_strains()]

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
            submission_form.project_uuid,
            submission_form.study_uuid,
        )

        return send_file(
            io.BytesIO(spreadsheet),
            as_attachment=True,
            download_name="template_study.xlsx",
        )


def upload_step4_page():
    with get_session() as db_session:
        submission_form = SubmissionForm(session.get('submission', {}), step=4, db_conn=db_session)
        errors = []

        if request.method == 'POST':
            with tempfile.TemporaryDirectory() as yml_dir:
                study_template = request.files['study-template'].read()
                data_template = request.files['data-template'].read()

                # TODO (2025-01-30) Check for project name and study name uniqueness

                errors = validate_upload(yml_dir, study_template, data_template)

                if len(errors) == 0:
                    (study_id, errors, errors_logic, studyUniqueID, projectUniqueID, project_id) = \
                        save_submission_to_database(db_session, yml_dir, submission_form, data_template)

                    if len(errors) == 0:
                        # TODO (2025-01-30) Message that data was successfully
                        # stored, reset submission. (Later, store submission as
                        # draft?)
                        #
                        # st.success(f"""Thank you! your study has been successfully uploaded into our database,
                        #         **Private Study ID**: {studyUniqueID} and **Study ID**: {study_id},
                        #         **Private Project Id**: {projectUniqueID} and **Project ID**: {project_id}""")

                        save_chart_data_to_files(study_id, data_template)
                        _save_chart_data_to_database(db_session, study_id, data_template)

                        return redirect(url_for('upload_step5_page'))

        return render_template(
            "pages/upload/index.html",
            submission_form=submission_form,
            errors=errors,
        )


def upload_spreadsheet_preview_fragment():
    file = request.files['file']
    sheets = spreasheet_preview.generate_preview(file)

    file_length = humanize.naturalsize(file.seek(0, os.SEEK_END))
    file.seek(0, os.SEEK_SET)

    return render_template(
        "pages/upload/step4/spreadsheet_preview.html",
        file=file,
        file_length=file_length,
        sheets=sheets
    )


def upload_step5_page():
    with get_connection() as conn:
        submission_form = SubmissionForm(session.get('submission', {}), step=5, db_conn=conn)

        return render_template(
            "pages/upload/index.html",
            submission_form=submission_form,
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



import io

from flask import (
    g,
    render_template,
    session,
    request,
    redirect,
    url_for,
    send_file,
)
import sqlalchemy as sql

from models import (
    Submission,
    ExcelFile,
    Project,
    ProjectUser,
    Study,
    StudyUser,
)
from forms.submission_form import SubmissionForm
from forms.upload_step2_form import UploadStep2Form
from forms.upload_step3_form import UploadStep3Form
from forms.upload_step4_form import UploadStep4Form
from forms.upload_step5_form import UploadStep5Form
from lib.submission_process import persist_submission_to_database

import legacy.study_spreadsheet as study_spreadsheet
import legacy.data_spreadsheet as data_spreadsheet


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


def upload_step4_page():
    submission_form = _init_submission_form(step=4)
    submission = submission_form.submission

    if request.method == 'POST':
        form = UploadStep4Form(request.form)

        submission_form.update_study_design(form.data)
        session['submission_id'] = submission_form.save()

        return redirect(url_for('upload_step5_page'))

    else:
        upload_form = UploadStep4Form(data=submission.studyDesign)

        return render_template(
            "pages/upload/index.html",
            submission_form=submission_form,
            submission=submission_form.submission,
            upload_form=upload_form,
        )


def upload_step5_page():
    submission_form = _init_submission_form(step=5)
    submission = submission_form.submission

    if request.method == 'POST':
        form = UploadStep5Form(request.form)

        submission_form.update_study_design(form.data)
        session['submission_id'] = submission_form.save()

        if _request_is_ajax():
            return render_template(
                "pages/upload/step5/_subform_list.html",
                submission_form=submission_form,
                upload_form=form,
            )
        else:
            return redirect(url_for('upload_step6_page'))

    else:
        upload_form = UploadStep5Form(data=submission.studyDesign)

        return render_template(
            "pages/upload/index.html",
            submission_form=submission_form,
            submission=submission_form.submission,
            upload_form=upload_form,
        )


def upload_step6_page():
    submission_form = _init_submission_form(step=6)
    submission = submission_form.submission
    errors = []

    if request.method == 'POST':
        if request.files['study-template']:
            submission.studyFile = ExcelFile.from_upload(request.files['study-template'])
        if request.files['data-template']:
            submission.dataFile  = ExcelFile.from_upload(request.files['data-template'])

        submission_form.save()

        errors = persist_submission_to_database(submission_form)

        if not errors:
            return redirect(url_for('upload_step7_page'))

    return render_template(
        "pages/upload/index.html",
        submission_form=submission_form,
        submission=submission_form.submission,
        errors=errors,
    )


def download_study_template_xlsx():
    submission_form = _init_submission_form(step=7)
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


def upload_spreadsheet_preview_fragment():
    excel_file = ExcelFile.from_upload(request.files['file'])

    return render_template(
        "pages/upload/step4/spreadsheet_preview.html",
        excel_file=excel_file,
    )


def upload_step7_page():
    submission_form = _init_submission_form(step=7)

    if request.method == 'POST':
        study = submission_form.submission.study

        if study and study.isPublishable:
            study.publish()
            g.db_session.add(study)
            g.db_session.commit()

            return redirect(url_for('study_show_page', studyId=study.publicId))

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

def _request_is_ajax():
    return request.headers.get('X-Requested-With', '') == 'XMLHttpRequest'

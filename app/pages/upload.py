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

from app.model.orm import ExcelFile
import app.model.lib.data_spreadsheet as data_spreadsheet
from app.model.lib.submission_process import (
    persist_submission_to_database,
    validate_data_file,
)
from app.model.lib.errors import LoginRequired
from app.view.forms.submission_form import SubmissionForm
from app.view.forms.upload_step2_form import UploadStep2Form
from app.view.forms.upload_step3_form import UploadStep3Form
from app.view.forms.upload_step4_form import UploadStep4Form
from app.view.forms.upload_step5_form import UploadStep5Form


def upload_status_page():
    submission_form = _init_submission_form(step=0)

    if g.current_user and g.current_user.uuid:
        user_submissions = g.current_user.submissions
    else:
        user_submissions = None

    return render_template(
        "pages/upload/index.html",
        submission_form=submission_form,
        user_submissions=user_submissions,
    )


def upload_step1_page():
    submission_form = _init_submission_form(step=1)

    if request.method == 'POST':
        submission_form.update_project(request.form)

        if len(submission_form.errors) == 0:
            session['submission_id'] = submission_form.save()
            return redirect(url_for('upload_step2_page'))

    return render_template(
        "pages/upload/index.html",
        submission_form=submission_form,
    )


def upload_step2_page():
    submission_form = _init_submission_form(step=2)
    upload_form     = _init_upload_form(UploadStep2Form, submission_form.submission)

    if _request_is_ajax():
        return _step2_partial(upload_form, submission_form)

    if request.method == 'POST':
        submission_form.update_strains(upload_form.data)

        if upload_form.validate():
            session['submission_id'] = submission_form.save()
            return redirect(url_for('upload_step3_page'))

    return render_template(
        "pages/upload/index.html",
        submission_form=submission_form,
        upload_form=upload_form,
    )


def _step2_partial(upload_form, submission_form):
    submission_form.update_strains(upload_form.data)

    if upload_form.validate():
        session['submission_id'] = submission_form.save()

    return render_template(
        "pages/upload/step2/_subform_list.html",
        submission_form=submission_form,
        upload_form=upload_form,
    )


def upload_step3_page():
    submission_form = _init_submission_form(step=3)
    upload_form     = _init_upload_form(UploadStep3Form, submission_form.submission)

    if _request_is_ajax():
        return _step3_partial(upload_form, submission_form)

    if request.method == 'POST':
        submission_form.update_study_design(upload_form.data)

        if upload_form.validate():
            session['submission_id'] = submission_form.save()
            return redirect(url_for('upload_step4_page'))

    return render_template(
        "pages/upload/index.html",
        submission_form=submission_form,
        upload_form=upload_form,
    )


def _step3_partial(upload_form, submission_form):
    submission_form.update_study_design(upload_form.data)

    if upload_form.validate():
        session['submission_id'] = submission_form.save()

    return render_template(
        "pages/upload/step3/_subform_list.html",
        submission_form=submission_form,
        upload_form=upload_form,
    )


def upload_step4_page():
    submission_form = _init_submission_form(step=4)
    upload_form     = _init_upload_form(UploadStep4Form, submission_form.submission)

    if _request_is_ajax():
        return _step4_partial(upload_form, submission_form, request.args['subform_type'])

    if request.method == 'POST':
        submission_form.update_study_design(upload_form.data)

        if upload_form.validate():
            session['submission_id'] = submission_form.save()
            return redirect(url_for('upload_step5_page'))

    return render_template(
        "pages/upload/index.html",
        submission_form=submission_form,
        upload_form=upload_form,
    )


def _step4_partial(upload_form, submission_form, subform_type):
    submission_form.update_study_design(upload_form.data)

    if upload_form.validate():
        session['submission_id'] = submission_form.save()

    return render_template(
        f"pages/upload/step4/_{subform_type}_subform_list.html",
        submission_form=submission_form,
        upload_form=upload_form,
    )


def upload_step5_page():
    submission_form = _init_submission_form(step=5)
    upload_form     = _init_upload_form(UploadStep5Form, submission_form.submission)

    if _request_is_ajax():
        return _step5_partial(upload_form, submission_form)

    if request.method == 'POST':
        submission_form.update_study_design(upload_form.data)

        if upload_form.validate():
            session['submission_id'] = submission_form.save()
            return redirect(url_for('upload_step6_page'))

    return render_template(
        "pages/upload/index.html",
        submission_form=submission_form,
        upload_form=upload_form,
    )


def _step5_partial(upload_form, submission_form):
    submission_form.update_study_design(upload_form.data)

    if upload_form.validate():
        session['submission_id'] = submission_form.save()

    return render_template(
        "pages/upload/step5/_subform_list.html",
        submission_form=submission_form,
        upload_form=upload_form,
    )


def upload_step6_page():
    submission_form = _init_submission_form(step=6)
    submission = submission_form.submission
    errors = []

    if request.method == 'POST':
        if request.files['data-template']:
            submission.dataFile = ExcelFile.from_upload(request.files['data-template'])
        submission_form.save()

        if not submission.dataFile:
            errors = ["No data file uploaded"]

        if not errors:
            errors = validate_data_file(submission_form)

        if not errors:
            errors = persist_submission_to_database(submission_form)

        if not errors:
            return redirect(url_for('upload_step7_page'))
    else:
        errors = validate_data_file(submission_form)

    return render_template(
        "pages/upload/index.html",
        submission_form=submission_form,
        errors=errors,
    )


def download_data_template_xlsx():
    submission_form = _init_submission_form(step=6)
    submission      = submission_form.submission

    metabolite_names = [m.name for m in submission_form.fetch_all_metabolites()]
    strain_names = [t.name for t in submission_form.fetch_taxa()]
    strain_names += [s['name'] for s in submission.studyDesign['custom_strains']]

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
    submission_form = _init_submission_form(step=6)

    excel_file = ExcelFile.from_upload(request.files['file'])
    errors = validate_data_file(submission_form, excel_file)

    return render_template(
        "pages/upload/step6/spreadsheet_preview.html",
        excel_file=excel_file,
        errors=errors,
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
    )


def _init_submission_form(step):
    if g.current_user is None and step != 0:
        raise LoginRequired()

    if g.current_user:
        user_uuid = g.current_user.uuid
    else:
        user_uuid = None

    return SubmissionForm(
        session.get('submission_id', None),
        step=step,
        db_session=g.db_session,
        user_uuid=user_uuid,
    )


def _init_upload_form(form_class, submission):
    if request.method == 'POST':
        return form_class(request.form)
    else:
        return form_class(data=submission.studyDesign)


def _request_is_ajax():
    return request.headers.get('X-Requested-With', '') == 'XMLHttpRequest'

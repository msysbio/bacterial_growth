from uuid import uuid4

from flask import render_template, session, request, redirect, url_for


def upload_index_page(step=1):
    return render_template(
        "pages/upload/index.html",
        step=step,
    )

def submit_step_1_upload():
    submission_type = request.form['submission-type']

    if submission_type == 'new-project':
        session['project_uuid'] = uuid4()
        session['study_uuid']   = uuid4()

        session['project'] = {
            'name':        request.form['project-name'],
            'description': request.form['project-description'],
        }
    elif submission_type == 'new-study':
        # TODO (2024-09-19) Validate project uuid in database
        session['project_uuid'] = request.form['project-uuid']
        session['study_uuid']   = uuid4()

        session['project'] = {
            'name':        f"[TODO] Name of project {session['project-uuid']}",
            'description': f"[TODO] Description of project {session['project-uuid']}",
        }
    elif submission_type == 'update-study':
        # TODO (2024-09-19) Validate project and study uuid in database
        session['project_uuid'] = request.form['project-uuid']
        session['study_uuid']   = request.form['study-uuid']

        session['project'] = {
            'name':        f"[TODO] Name of project {session['project-uuid']}",
            'description': f"[TODO] Description of project {session['project-uuid']}",
        }
    else:
        raise KeyError("Unknown submission type: {}".format(submission_type))

    return redirect(url_for('upload_index_page', step=2))

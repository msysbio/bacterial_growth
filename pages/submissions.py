from flask import (
    g,
    session,
    redirect,
    url_for,
)
import sqlalchemy as sql

from models import Submission


def new_submission_action():
    if 'submission_id' in session:
        del session['submission_id']

    return redirect(url_for('upload_step1_page'))


def edit_submission_action(id):
    session['submission_id'] = id

    return redirect(url_for('upload_status_page'))


def delete_submission_action(id):
    if 'submission_id' in session and session['submission_id'] == id:
        del session['submission_id']

    g.db_session.execute(sql.delete(Submission).where(Submission.id == id))
    g.db_session.commit()

    return redirect(url_for('upload_status_page'))

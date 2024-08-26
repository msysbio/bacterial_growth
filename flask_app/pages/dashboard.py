from flask import render_template, request
import sqlalchemy as sql

from flask_app.db import get_connection


def dashboard_index_page():
    studyName = None
    studyId = request.args.get('studyId')

    with get_connection() as conn:
        if studyId:
            query = "SELECT studyName FROM Study WHERE studyId = :studyId LIMIT 1"
            studyName = conn.execute(sql.text(query), { 'studyId': studyId }).scalar()

        return render_template(
            "pages/dashboard.html",
            studyId=studyId,
            studyName=studyName,
        )

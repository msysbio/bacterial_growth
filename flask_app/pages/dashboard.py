from flask import render_template, request
import sqlalchemy as sql

from flask_app.db import get_connection
from flask_app.models.study_dfs import get_experiments


def dashboard_index_page():
    studyName = None
    studyId = request.args.get('studyId')
    experiments = []

    with get_connection() as conn:
        if studyId:
            query = "SELECT studyName FROM Study WHERE studyId = :studyId LIMIT 1"
            studyName = conn.execute(sql.text(query), { 'studyId': studyId }).scalar()

            df_experiments = get_experiments(studyId, conn)
            experiments = zip(
                df_experiments["experimentId"],
                df_experiments["experimentDescription"],
                [b_ids.split(',') for b_ids in df_experiments["bioreplicateIds"]]
            )

        return render_template(
            "pages/dashboard/index.html",
            studyId=studyId,
            studyName=studyName,
            experiments=experiments,
        )

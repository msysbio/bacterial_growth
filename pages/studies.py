from flask import (
    g,
    render_template,
    send_file,
    request,
)
import sqlalchemy as sql

from db import get_connection, get_session
import models.study_dfs as study_dfs
from models import Study
from forms.experiment_export_form import ExperimentExportForm
import lib.util as util


def study_show_page(studyId):
    study = g.db_session.scalars(
        sql.select(Study)
        .where(Study.studyId == studyId)
        .limit(1)
    ).one()

    if study.visibleToUser(g.current_user):
        return render_template("pages/studies/show.html", study=study)
    else:
        return render_template("pages/studies/_show_unpublished.html", study=study)


def study_export_page(studyId):
    with get_session() as db_session:
        study = db_session.scalars(
            sql.select(Study)
            .where(Study.studyId == studyId)
            .limit(1)
        ).one()

        return render_template(
            "pages/studies/export.html",
            study=study,
            studyId=studyId,
        )


def study_export_preview_fragment(studyId):
    with get_session() as db_session:
        csv_previews = []
        export_form = ExperimentExportForm(studyId, db_session, request.args)
        experiment_data = export_form.get_experiment_data()

        for experiment, experiment_df in experiment_data.items():
            csv = experiment_df[:5].to_csv(index=False, sep=export_form.csv_separator)
            csv_previews.append(f"""
                <h3>{experiment.experimentId}.csv ({len(experiment_df)} rows)</h3>
                <pre>{csv}</pre>
            """)

        return '\n'.join(csv_previews)


def study_download_zip(studyId):
    with get_session() as db_session:
        csv_data = []

        export_form = ExperimentExportForm(studyId, db_session, request.args)
        experiment_data = export_form.get_experiment_data()

        for experiment, experiment_df in experiment_data.items():
            csv_bytes = experiment_df.to_csv(index=False, sep=export_form.csv_separator)
            csv_name = f"{experiment.experimentId}.csv"

            csv_data.append((csv_name, csv_bytes))

        study = study_dfs.get_general_info(studyId, db_session)
        readme_text = render_template(
            'pages/studies/export_readme.md',
            study=study,
            experiments=experiment_data.keys(),
        )
        csv_data.append(('README.md', readme_text.encode('utf-8')))

        zip_file = util.createzip(csv_data)

        return send_file(
            zip_file,
            as_attachment=True,
            download_name=f"{studyId}.zip",
        )

from flask import (
    g,
    render_template,
    send_file,
    request,
)
from werkzeug.exceptions import Forbidden
import sqlalchemy as sql

from db import get_connection, get_session
import models.study_dfs as study_dfs
from models import Study
from forms.experiment_export_form import ExperimentExportForm
import lib.util as util


def study_show_page(studyId):
    study = _fetch_study(studyId, check_user=False)

    if study.visibleToUser(g.current_user):
        return render_template("pages/studies/show.html", study=study)
    else:
        return render_template("pages/studies/_show_unpublished.html", study=study)


def study_export_page(studyId):
    study = _fetch_study(studyId)

    return render_template(
        "pages/studies/export.html",
        study=study,
        studyId=studyId,
    )


def study_export_preview_fragment(studyId):
    # We only need the id here, but we call it to apply visibility checks:
    _study = _fetch_study(studyId)

    csv_previews = []
    export_form = ExperimentExportForm(g.db_session, request.args)
    experiment_data = export_form.get_experiment_data()

    for experiment, experiment_df in experiment_data.items():
        csv = experiment_df[:5].to_csv(index=False, sep=export_form.csv_separator)
        csv_previews.append(f"""
            <h3>{experiment.experimentId}.csv ({len(experiment_df)} rows)</h3>
            <pre>{csv}</pre>
        """)

    return '\n'.join(csv_previews)


def study_download_zip(studyId):
    csv_data = []

    export_form = ExperimentExportForm(studyId, g.db_session, request.args)
    experiment_data = export_form.get_experiment_data()

    for experiment, experiment_df in experiment_data.items():
        csv_bytes = experiment_df.to_csv(index=False, sep=export_form.csv_separator)
        csv_name = f"{experiment.experimentId}.csv"

        csv_data.append((csv_name, csv_bytes))

    study = study_dfs.get_general_info(studyId, g.db_session)
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

def _fetch_study(studyId, check_user=True):
    study = g.db_session.scalars(
        sql.select(Study)
        .where(Study.studyId == studyId)
        .limit(1)
    ).one()

    if not study.visibleToUser(g.current_user):
        raise Forbidden()

    return study

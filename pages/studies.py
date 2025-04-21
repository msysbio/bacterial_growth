from flask import (
    g,
    render_template,
    send_file,
    request,
)
from werkzeug.exceptions import Forbidden
import sqlalchemy as sql

import models.study_dfs as study_dfs
from models import (
    Study,
    Experiment,
)
from forms.experiment_export_form import ExperimentExportForm
from forms.experiment_chart_form import ExperimentChartForm
import lib.util as util


def study_show_page(studyId):
    study = _fetch_study(studyId, check_user_visibility=False)

    if study.visible_to_user(g.current_user):
        return render_template("pages/studies/show.html", study=study)
    else:
        return render_template("pages/studies/show_unpublished.html", study=study)


def study_manage_page(studyId):
    study = _fetch_study(studyId)
    if not study.manageable_by_user(g.current_user):
        raise Forbidden()

    return render_template("pages/studies/manage.html", study=study)


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


def study_visualize_page(studyId):
    study = _fetch_study(studyId)
    experiment_forms = [ExperimentChartForm(e) for e in study.experiments]

    return render_template(
        "pages/studies/visualize.html",
        study=study,
        experiment_forms=experiment_forms,
    )


def study_chart_fragment(studyId):
    args = request.args.to_dict()

    width = args.pop('width')
    show_log_toggle = False

    experimentUniqueId = args.pop('experimentUniqueId')
    technique          = args.pop('technique')

    experiment = g.db_session.get(Experiment, experimentUniqueId)
    form       = ExperimentChartForm(experiment)

    if technique in ('16S rRNA-seq', 'FC counts per species'):
        show_log_toggle = True
        figs = form.generate_reads_figures(technique, args)
    elif technique == 'Metabolites':
        # TODO (2025-03-02) Separate "technique" and "subject type"
        figs = form.generate_metabolite_figures(technique, args)
    else:
        figs = form.generate_growth_figures(technique, args)

    fig_htmls = []
    for fig in figs:
        fig.update_layout(
            margin=dict(l=0, r=0, t=60, b=40),
            title=dict(x=0)
        )

        fig_htmls.append(fig.to_html(
            full_html=False,
            include_plotlyjs=False,
            default_width=f"{width}px",
        ))

    return render_template(
        'pages/studies/_figs.html',
        fig_htmls=fig_htmls,
        show_log_toggle=show_log_toggle
    )


def _fetch_study(studyId, check_user_visibility=True):
    study = g.db_session.scalars(
        sql.select(Study)
        .where(Study.studyId == studyId)
        .limit(1)
    ).one()

    if check_user_visibility and not study.visible_to_user(g.current_user):
        raise Forbidden()

    return study

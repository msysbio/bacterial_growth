from flask import (
    g,
    render_template,
    request,
)
import sqlalchemy as sql

from forms.experiment_chart_form import ExperimentChartForm
from models import (
    Study,
    Experiment,
)


def dashboard_index_page():
    studyId = request.args.get('studyId')
    study = None
    experiment_forms = []

    if studyId:
        study = g.db_session.scalars(
            sql.select(Study)
            .where(Study.studyId == studyId),
        ).one()

    if study:
        experiment_forms = [ExperimentChartForm(e) for e in study.experiments]

    return render_template(
        "pages/dashboard/index.html",
        studyId=studyId,
        study=study,
        experiment_forms=experiment_forms,
    )


def dashboard_chart_fragment():
    args = request.args.to_dict()

    width = args.pop('width')
    show_log_toggle = False

    _                  = args.pop('studyId')
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
        'pages/dashboard/_figs.html',
        fig_htmls=fig_htmls,
        show_log_toggle=show_log_toggle
    )

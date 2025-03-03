from flask import render_template, request
import sqlalchemy as sql

from db import get_session
from forms.experiment_chart_form import ExperimentChartForm
from models.study import Study
from models.experiment import Experiment


PLOTLY_TEMPLATE = 'plotly_white'


def dashboard_index_page():
    studyName        = None
    studyId          = request.args.get('studyId')
    experiment_forms = []

    with get_session() as db_session:
        if studyId:
            query = (
                sql.select(Experiment)
                .where(Experiment.studyId == studyId)
                .order_by(Experiment.experimentId)
            )
            experiment_forms = [ExperimentChartForm(e) for e in db_session.scalars(query).all()]
            studyName = db_session.get(Study, studyId).studyName

        return render_template(
            "pages/dashboard/index.html",
            studyId=studyId,
            studyName=studyName,
            experiment_forms=experiment_forms,
        )


def dashboard_chart_fragment():
    args = request.args.to_dict()

    width = args.pop('width')
    show_log_toggle = False

    _                  = args.pop('studyId')
    experimentUniqueId = args.pop('experimentUniqueId')
    technique          = args.pop('technique')

    with get_session() as db_session:
        experiment = db_session.get(Experiment, experimentUniqueId)
        form       = ExperimentChartForm(experiment)

        if technique in ('16S rRNA-seq', 'FC per species'):
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

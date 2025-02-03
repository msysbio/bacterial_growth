from flask import render_template, request
import sqlalchemy as sql
from db import get_connection
from forms.experiment_chart_form import ExperimentChartForm
from models.study_dfs import get_experiments
from models.experiment import get_experiment
from legacy.chart_data import get_chart_data


def dashboard_index_page():
    studyName        = None
    studyId          = request.args.get('studyId')
    experiment_forms = []

    with get_connection() as conn:
        if studyId:
            query = "SELECT studyName FROM Study WHERE studyId = :studyId LIMIT 1"
            studyName = conn.execute(sql.text(query), {'studyId': studyId}).scalar()

            df_experiments = get_experiments(studyId, conn)
            experiment_forms = ExperimentChartForm.from_df(studyId, df_experiments)

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

    studyId      = args.pop('studyId')
    experimentId = args.pop('experimentId')
    measurement  = args.pop('measurement')

    with get_connection() as conn:
        experiment          = get_experiment(experimentId, conn)
        df_growth, df_reads = get_chart_data(studyId)

        form = ExperimentChartForm(df_growth, df_reads, experiment)

        if measurement == 'Reads 16S rRNA Seq':
            show_log_toggle = True
            figs = form.generate_reads_figures('reads', args)
        elif measurement == 'FC counts per species':
            show_log_toggle = True
            figs = form.generate_reads_figures('counts', args)
        elif measurement == 'Metabolites':
            figs = form.generate_metabolite_figures(args)
        else:
            figs = form.generate_growth_figures(measurement, args)

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

from flask import render_template, request
import sqlalchemy as sql
from flask_app.db import get_connection
from flask_app.forms.experiment_chart_form import ExperimentChartForm
from flask_app.models.study_dfs import get_experiments
from flask_app.models.experiment_dfs import get_experiment
from flask_app.lib.hack import get_chart_data


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

    studyId      = args.pop('studyId')
    experimentId = args.pop('experimentId')
    measurement  = args.pop('measurement')

    with get_connection() as conn:
        experiment          = get_experiment(experimentId, conn)
        df_growth, df_reads = get_chart_data(studyId)

        form = ExperimentChartForm(df_growth, df_reads, experiment)

        # TODO (2024-09-09) Reads and FC counts are different, add another
        # "reads" function, determine which to show based on reads CSV keys

        if measurement == 'Reads 16S rRNA Seq':
            figs = form.generate_reads_figures(args)
        elif measurement == 'Metabolites':
            figs = form.generate_metabolite_figures(args)
        else:
            figs = form.generate_growth_figures(measurement, args)

        fig_htmls = [
            fig.to_html(
                full_html=False,
                include_plotlyjs=False,
                default_width=f"{width}px",
            )
            for fig in figs
        ]

        return render_template('pages/dashboard/_figs.html', fig_htmls=fig_htmls)


def generate_reads_figures(studyId, experimentId, args):
    return []

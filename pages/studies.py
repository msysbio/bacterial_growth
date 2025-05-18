from flask import (
    g,
    render_template,
    send_file,
    request,
)
from werkzeug.exceptions import Forbidden
import pandas as pd
import sqlalchemy as sql
from sqlalchemy.sql.expression import literal

import models.study_dfs as study_dfs
from models import (
    Experiment,
    Measurement,
    MeasurementTechnique,
    MeasurementContext,
    ModelingRequest,
    ModelingResult,
    Study,
)
from forms.experiment_export_form import ExperimentExportForm
from forms.study_chart_form import StudyChartForm
from forms.study_modeling_form import StudyModelingForm
from lib.chart import Chart
from lib.modeling_tasks import process_modeling_request
from lib.figures import make_figure_with_traces
from lib.db import execute_into_df
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

    modeling_form = StudyModelingForm(g.db_session, study)

    return render_template(
        "pages/studies/manage.html",
        study=study,
        modeling_form=modeling_form,
    )


def study_export_page(studyId):
    study = _fetch_study(studyId)

    return render_template(
        "pages/studies/export.html",
        study=study,
        studyId=studyId,
    )


def study_export_preview_fragment(studyId):
    # We only need the id here, but we call it to apply visibility checks:
    _fetch_study(studyId)

    csv_previews = []
    export_form = ExperimentExportForm(g.db_session, request.args)
    experiment_data = export_form.get_experiment_data()

    for experiment, experiment_df in experiment_data.items():
        csv = experiment_df[:5].to_csv(index=False, sep=export_form.csv_separator)
        csv_previews.append(f"""
            <h3>{experiment.name}.csv ({len(experiment_df)} rows)</h3>
            <pre>{csv}</pre>
        """)

    return '\n'.join(csv_previews)


def study_download_zip(studyId):
    csv_data = []

    export_form = ExperimentExportForm(g.db_session, request.args)
    experiment_data = export_form.get_experiment_data()

    for experiment, experiment_df in experiment_data.items():
        csv_bytes = experiment_df.to_csv(index=False, sep=export_form.csv_separator)
        csv_name = f"{experiment.name}.csv"

        csv_data.append((csv_name, csv_bytes))

    study = g.db_session.scalars(sql.select(Study).where(Study.studyId == studyId)).one()
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
    study      = _fetch_study(studyId)
    chart_form = StudyChartForm(g.db_session, study)

    return render_template(
        "pages/studies/visualize.html",
        study=study,
        chart_form=chart_form,
    )


def study_chart_fragment(studyId):
    study = _fetch_study(studyId)
    args = request.form.to_dict()

    width = request.args.get('width', None)

    chart_form = StudyChartForm(g.db_session, study)
    chart = chart_form.build_chart(args, width)

    return render_template(
        'pages/studies/visualize/_chart.html',
        chart_form=chart_form,
        chart=chart,
    )


def study_modeling_submit_action(studyId):
    args = request.form.to_dict()

    study = _fetch_study(studyId)
    width = request.args.get('width', None)

    chart_form = StudyModelingForm(g.db_session, study)
    chart = chart_form.build_chart(args, width)

    if chart.selected_measurement_context_id:
        modeling_request = g.db_session.scalars(
            sql.select(ModelingRequest)
            .where(
                ModelingRequest.contextId == chart.selected_measurement_context_id,
                ModelingRequest.type == chart_form.modeling_type,
                ModelingRequest.studyId == study.publicId,
            )
        ).one_or_none()

    if modeling_request is None:
        modeling_request = ModelingRequest(
            type=chart_form.modeling_type,
            study=study,
        )
        g.db_session.add(modeling_request)
        g.db_session.commit()

    result = process_modeling_request.delay(modeling_request.id, chart_form.measurement_context_ids)
    modeling_request.jobUuid = result.task_id
    g.db_session.commit()

    return {'modelingRequestId': modeling_request.id}


def study_modeling_check_json(studyId, modelingTechniqueId):
    modeling_technique = g.db_session.get(ModelingTechnique, modelingTechniqueId)

    return {
        "ready":      modeling_technique.state in ('ready', 'error'),
        "successful": modeling_technique.state != 'error',
    }


def study_modeling_chart_fragment(studyId, measurementContextId):
    study = _fetch_study(studyId)
    args = request.args.to_dict()

    modeling_type = args.pop('modelingType')
    width         = args.pop('width')
    height        = args.pop('height')

    measurement_context = g.db_session.get(MeasurementContext, measurementContextId)
    measurement_df      = measurement_context.get_df(g.db_session)

    chart = Chart(
        time_units=study.timeUnits,
        title=measurement_context.get_chart_label(g.db_session),
    )
    chart.add_df(measurement_df, units=measurement_context.technique.units, label="Measurements")

    modeling_result = g.db_session.scalars(
        sql.select(ModelingResult)
        .join(ModelingRequest)
        .where(
            ModelingRequest.type == modeling_type,
            ModelingResult.measurementContextId == measurement_context.id,
            ModelingResult.state.in_(('ready', 'error')),
        )
    ).one_or_none()

    if modeling_result:
        modeling_result.generate_chart_df(measurement_df)
        label = modeling_result.model_name

        chart.add_model_df(df, label)

        model_coefficients = modeling_result.coefficients
    else:
        model_coefficients = ModelingResult.empty_coefficients(modeling_type)

    return render_template(
        'pages/studies/manage/_modeling_chart.html',
        chart=chart,
        model_coefficients=model_coefficients,
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

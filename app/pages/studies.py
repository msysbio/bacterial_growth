import io

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

import app.model.lib.study_dfs as study_dfs
from app.model.orm import (
    Bioreplicate,
    Experiment,
    Measurement,
    MeasurementTechnique,
    MeasurementContext,
    ModelingRequest,
    ModelingResult,
    Study,
)
from app.view.forms.experiment_export_form import ExperimentExportForm
from app.view.forms.comparative_chart_form import ComparativeChartForm
from app.model.lib.chart import Chart
from app.model.lib.modeling_tasks import process_modeling_request
from app.model.lib.model_export import export_model_csv
from app.model.lib.figures import make_figure_with_traces
from app.model.lib.db import execute_into_df
from app.model.lib.log_transform import apply_log_transform
import app.model.lib.util as util


def study_show_page(studyId):
    study = _fetch_study(
        studyId,
        check_user_visibility=False,
        sql_options=(
            sql.orm.selectinload(
                Study.experiments,
                Experiment.bioreplicates,
                Bioreplicate.measurementContexts,
                MeasurementContext.technique,
            ),
            sql.orm.selectinload(
                Study.experiments,
                Experiment.bioreplicates,
                Bioreplicate.measurementContexts,
                MeasurementContext.measurements,
            ),
        )
    )

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


def study_download_data_zip(studyId):
    study = _fetch_study(studyId)
    csv_data = []

    export_form = ExperimentExportForm(g.db_session, request.args)
    experiment_data = export_form.get_experiment_data()

    for experiment, experiment_df in experiment_data.items():
        csv_bytes = experiment_df.to_csv(index=False, sep=export_form.csv_separator)
        csv_name = f"{experiment.name}.csv"

        csv_data.append((csv_name, csv_bytes))

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


def study_download_models_csv(studyId):
    study = _fetch_study(studyId)

    csv_data = export_model_csv(g.db_session, study)

    return send_file(
        io.BytesIO(csv_data),
        as_attachment=True,
        download_name=f"{studyId}_models.csv",
    )

def study_visualize_page(studyId):
    study = _fetch_study(studyId)

    left_axis_ids  = [int(s) for s in request.args.get('l', '').split(',') if s != '']
    right_axis_ids = [int(s) for s in request.args.get('r', '').split(',') if s != '']

    chart_form = ComparativeChartForm(
        g.db_session,
        time_units=study.timeUnits,
        left_axis_ids=left_axis_ids,
        right_axis_ids=right_axis_ids,
    )

    return render_template(
        "pages/studies/visualize.html",
        study=study,
        chart_form=chart_form,
    )


def study_chart_fragment(studyId):
    study = _fetch_study(studyId)
    args = request.form.to_dict()

    width = request.args.get('width', None)

    chart_form = ComparativeChartForm(g.db_session, time_units=study.timeUnits)
    chart = chart_form.build_chart(args, width)

    return render_template(
        'pages/studies/visualize/_chart.html',
        chart_form=chart_form,
        chart=chart,
        study=study,
    )


def study_modeling_submit_action(studyId):
    study = _fetch_study(studyId)
    args = request.form.to_dict()

    modeling_type = args.pop('modelingType')
    measurement_context_id = int(args.pop('selectedContext').removeprefix('measurementContext|'))

    modeling_request = g.db_session.scalars(
        sql.select(ModelingRequest)
        .where(
            ModelingRequest.type == modeling_type,
            ModelingRequest.studyId == study.publicId,
        )
    ).one_or_none()

    if modeling_request is None:
        modeling_request = ModelingRequest(
            type=modeling_type,
            study=study,
        )
        g.db_session.add(modeling_request)
        g.db_session.commit()

    result = process_modeling_request.delay(modeling_request.id, [measurement_context_id], args)
    modeling_request.jobUuid = result.task_id
    g.db_session.commit()

    return {'modelingRequestId': modeling_request.id}


def study_modeling_check_json(studyId):
    study = _fetch_study(studyId)

    # TODO (2025-05-20) Return counts of pending requests?

    ready      = all([mr.state in ('ready', 'error') for mr in study.modelingRequests])
    successful = all([mr.state != 'error' for mr in study.modelingRequests])

    return {
        "ready":      ready,
        "successful": successful,
    }


def study_modeling_chart_fragment(studyId, measurementContextId):
    study = _fetch_study(studyId)
    args = request.args.to_dict()

    modeling_type = args.pop('modelingType')
    width         = args.pop('width')
    height        = args.pop('height')
    log_transform = args.pop('logTransform', 'false') == 'true'

    measurement_context = g.db_session.get(MeasurementContext, measurementContextId)
    measurement_df      = measurement_context.get_df(g.db_session)

    chart = Chart(
        time_units=study.timeUnits,
        title=measurement_context.get_chart_label(g.db_session),
        legend_position='right',
        log_left=log_transform,
    )
    units = measurement_context.technique.units
    if units == '':
        units = measurement_context.technique.short_name

    if log_transform:
        apply_log_transform(measurement_df)

    chart.add_df(
        measurement_df,
        units=units,
        label="Measurements",
    )

    modeling_result = g.db_session.scalars(
        sql.select(ModelingResult)
        .join(ModelingRequest)
        .where(
            ModelingRequest.type == modeling_type,
            ModelingResult.measurementContextId == measurement_context.id,
            ModelingResult.state == 'ready',
        )
    ).one_or_none()

    if modeling_result:
        df = modeling_result.generate_chart_df(measurement_df)
        if log_transform:
            apply_log_transform(df)

        label = modeling_result.model_name
        chart.add_model_df(df, units=units, label=label)

        model_inputs       = modeling_result.inputs
        model_coefficients = modeling_result.coefficients
        model_fit          = modeling_result.fit
        r_summary          = modeling_result.rSummary
    else:
        model_inputs       = ModelingResult.empty_inputs(modeling_type)
        model_coefficients = ModelingResult.empty_coefficients(modeling_type)
        model_fit          = ModelingResult.empty_fit()
        r_summary          = None

    return render_template(
        'pages/studies/manage/_modeling_chart.html',
        chart=chart,
        form_data=request.form,
        model_type=modeling_type,
        model_inputs=model_inputs,
        model_coefficients=model_coefficients,
        model_fit=model_fit,
        r_summary=r_summary,
        measurement_context=measurement_context,
        log_transform=log_transform,
    )


def _fetch_study(studyId, check_user_visibility=True, sql_options=None):
    sql_options = sql_options or ()

    study = g.db_session.scalars(
        sql.select(Study)
        .where(Study.studyId == studyId)
        .options(*sql_options)
        .limit(1)
    ).one()

    if check_user_visibility and not study.visible_to_user(g.current_user):
        raise Forbidden()

    return study

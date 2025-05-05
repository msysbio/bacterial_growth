from flask import (
    g,
    render_template,
    send_file,
    request,
)
from werkzeug.exceptions import Forbidden
import sqlalchemy as sql
from sqlalchemy.sql.expression import literal
from celery.result import AsyncResult as CeleryResult

import models.study_dfs as study_dfs
from models import (
    Study,
    Experiment,
    Measurement,
    MeasurementTechnique,
    CalculationTechnique,
    Calculation,
)
from forms.experiment_export_form import ExperimentExportForm
from forms.experiment_chart_form import ExperimentChartForm
from lib.calculation_tasks import update_calculation_technique
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
            <h3>{experiment.name}.csv ({len(experiment_df)} rows)</h3>
            <pre>{csv}</pre>
        """)

    return '\n'.join(csv_previews)


def study_download_zip(studyId):
    csv_data = []

    export_form = ExperimentExportForm(studyId, g.db_session, request.args)
    experiment_data = export_form.get_experiment_data()

    for experiment, experiment_df in experiment_data.items():
        csv_bytes = experiment_df.to_csv(index=False, sep=export_form.csv_separator)
        csv_name = f"{experiment.name}.csv"

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

    experiment_id = args.pop('experimentUniqueId')
    technique     = args.pop('technique')

    experiment = g.db_session.get(Experiment, experiment_id)
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


def study_calculations_action(studyId):
    args = request.form.to_dict()

    study = _fetch_study(studyId)
    calculation_type = args['type']

    target_param_list = []
    for target_identifier in args.keys():
        if not target_identifier.startswith('target|'):
            continue

        (
            _label,
            bioreplicate_uuid,
            measurement_technique_id,
            subject_type,
            subject_id,
        ) = target_identifier.split('|')

        target_param_list.append({
            'bioreplicate_uuid':        bioreplicate_uuid,
            'measurement_technique_id': measurement_technique_id,
            'subject_type':             subject_type,
            'subject_id':               subject_id,
        })

    calculation_technique = g.db_session.scalars(
        sql.select(CalculationTechnique)
        .where(
            CalculationTechnique.type == calculation_type,
            CalculationTechnique.studyUniqueID == study.uuid
        )
    ).one_or_none()
    if calculation_technique is None:
        calculation_technique = CalculationTechnique(
            type=calculation_type,
            studyUniqueID=study.uuid,
        )
        g.db_session.add(calculation_technique)
        g.db_session.commit()

    result = update_calculation_technique.delay(calculation_technique.id, target_param_list)
    calculation_technique.jobUuid = result.task_id
    g.db_session.commit()

    return {'calculationTechniqueId': calculation_technique.id}


def study_calculations_check_json(studyId, calculationTechniqueId):
    calculation_technique = g.db_session.get(CalculationTechnique, calculationTechniqueId)

    return {
        "ready":      calculation_technique.state in ('ready', 'error'),
        "successful": calculation_technique.state != 'error',
    }


def study_calculations_edit_fragment(studyId):
    args = request.args.to_dict()

    calculation_type = args.pop('calculationType')
    biorep_uuid      = args.pop('bioreplicateUniqueId')
    subject_type     = args.pop('subjectType')
    subject_id       = args.pop('subjectId')
    technique_id     = args.pop('techniqueId')

    width  = args.pop('width')
    height = args.pop('height')

    measurement_technique = g.db_session.get(MeasurementTechnique, technique_id)
    subject = Measurement.get_subject(g.db_session, subject_id, subject_type)

    measurement_df = execute_into_df(
        g.db_session,
        sql.select(
            Measurement.timeInHours.label("time"),
            Measurement.value.label("value"),
            (literal(subject.name) + ' ' + literal(measurement_technique.short_name)).label("name"),
        )
        .where(
            Measurement.bioreplicateUniqueId == biorep_uuid,
            Measurement.subjectType == subject_type,
            Measurement.subjectId == subject_id,
            Measurement.techniqueId == technique_id,
        )
    )

    query = (
        sql.select(Calculation)
        .where(
            Calculation.type == calculation_type,
            Calculation.bioreplicateUniqueId == biorep_uuid,
            Calculation.subjectType == subject_type,
            Calculation.subjectId == subject_id,
            Calculation.measurementTechniqueId == measurement_technique.id,
            Calculation.state.in_(('ready', 'error')),
        )
    )
    calculation = g.db_session.scalars(query).one_or_none()

    if calculation:
        calculation_df = calculation.generate_chart_df(measurement_df)
        fig_dfs = [measurement_df, calculation_df]
    else:
        fig_dfs = [measurement_df]

    fig = make_figure_with_traces(
        fig_dfs,
        labels={
            'time': 'Hours',
            'value': measurement_technique.units,
        },
    )

    max_y = measurement_df['value'].max()
    std_y = measurement_df['value'].std()

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        title=dict(x=0),
        legend=dict(
            yanchor="bottom",
            xanchor="right",
        ),
        yaxis_range=[-std_y / 10, max_y + std_y / 2]
    )

    fig_html = fig.to_html(
        full_html=False,
        include_plotlyjs=False,
        default_width=f"{width}px",
        default_height=f"{height}px",
    )

    return render_template(
        'pages/studies/_calculation_result.html',
        calculation=calculation,
        fig_htmls=[fig_html],
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

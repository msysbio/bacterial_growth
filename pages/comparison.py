import json

from flask import (
    g,
    render_template,
    redirect,
    request,
    session,
)
import sqlalchemy as sql
from sqlalchemy.sql.expression import literal

from models import (
    Bioreplicate,
    Measurement,
    MeasurementTechnique,
)
from lib.db import execute_into_df
from lib.figures import make_figure_with_secondary_axis


def comparison_show_page():
    compare_data = _init_compare_data()

    targets = []
    for target_identifier in sorted(compare_data['targets']):
        (biorep_uuid, technique_id, subject_type, subject_id) = target_identifier.split('|')

        technique    = g.db_session.get(MeasurementTechnique, technique_id)
        bioreplicate = g.db_session.get(Bioreplicate, biorep_uuid)
        subject      = Measurement.get_subject(g.db_session, subject_id, subject_type)
        measurements = g.db_session.scalars(
            sql.select(Measurement)
            .where(
                Measurement.techniqueId == technique_id,
                Measurement.subjectId == subject_id,
                Measurement.subjectType == subject_type,
            )
        ).all()

        targets.append((target_identifier, bioreplicate, technique, subject, measurements))

    return render_template("pages/comparison/show.html", targets=targets)


def comparison_update_json(action):
    compare_data = _init_compare_data()
    target       = request.json['target']
    target_set   = set(compare_data['targets'])

    if action == 'add':
        target_set.add(target)
    elif action == 'remove':
        target_set.remove(target)
    else:
        raise ValueError(f"Unexpected action: {action}")

    compare_data['targets'] = list(target_set)
    session['compareData'] = compare_data

    return json.dumps({'targetCount': len(compare_data['targets'])})


def comparison_clear_action():
    if 'compareData' in session:
        del session['compareData']

    return redirect(request.referrer)


def comparison_chart_fragment():
    args = request.args.to_dict()

    width = args.pop('width')
    target_data = []

    for (target_identifier, direction) in args.items():
        (biorep_uuid, technique_id, subject_type, subject_id) = target_identifier.split('|')

        subject = Measurement.get_subject(g.db_session, subject_id, subject_type)
        technique = g.db_session.get(MeasurementTechnique, technique_id)

        measurement_query = (
            sql.select(
                Measurement.timeInHours.label("time"),
                Measurement.value.label("value"),
                (literal(subject.name) + ' ' + literal(technique.short_name)).label("name"),
            )
            .where(
                Measurement.bioreplicateUniqueId == biorep_uuid,
                Measurement.techniqueId == technique_id,
                Measurement.subjectId == subject_id,
                Measurement.subjectType == subject_type,
            )
        )
        df = execute_into_df(g.db_conn, measurement_query)
        target_data.append((direction, df))

    fig = make_figure_with_secondary_axis(target_data)
    fig.update_layout(
        margin=dict(l=0, r=0, t=60, b=40),
        title=dict(x=0)
    )
    fig_html = fig.to_html(
        full_html=False,
        include_plotlyjs=False,
        default_width=f"{width}px",
    )

    return render_template(
        'pages/comparison/_chart.html',
        fig_html=fig_html,
    )


def _init_compare_data():
    return session.get('compareData', {'targets': []})

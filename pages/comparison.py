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
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from models import (
    Bioreplicate,
    Measurement,
    MeasurementTechnique,
)
from lib.db import execute_into_df

PLOTLY_TEMPLATE = 'plotly_white'


def comparison_show_page():
    compare_data = session.get('compareData', {'targets': []})

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


def comparison_update_json():
    data = request.json
    data['targets'] = list(set(data['targets']))

    session['compareData'] = data

    return json.dumps({ 'targetCount': len(data['targets']) })

def comparison_clear_action():
    if 'compareData' in session:
        del session['compareData']

    return redirect(request.referrer)


def comparison_chart_fragment():
    args = request.args.to_dict()

    width = args.pop('width')
    target_identifiers = args.keys()
    target_data = []

    for (target_identifier, direction) in args.items():
        (biorep_uuid, technique_id, subject_type, subject_id) = target_identifier.split('|')

        subject = Measurement.get_subject(g.db_session, subject_id, subject_type)
        measurement_query = (
            sql.select(
                Measurement.timeInHours.label("time"),
                Measurement.value.label("value"),
                literal(subject.name).label("subjectName"),
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

    fig = _render_figure(target_data)
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
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

def _render_figure(data, **params):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    for direction, df in data:
        if direction == 'left':
            fig.add_trace(
                go.Scatter(x=df['time'], y=df['value'], name=df['subjectName'][0]),
                secondary_y=False,
            )
        elif direction == 'right':
            fig.add_trace(
                go.Scatter(x=df['time'], y=df['value'], name=df['subjectName'][0], line={'dash': 'dot'}),
                secondary_y=True,
            )
        else:
            raise ValueError(f"Unexpected direction received: {direction}")

    return fig

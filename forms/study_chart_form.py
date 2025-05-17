import plotly.express as px
import numpy as np
import pandas as pd
import sqlalchemy as sql
from sqlalchemy.sql.expression import literal_column

from db import get_connection, get_session
from lib.db import execute_into_df
from lib.chart import Chart
from models import (
    Experiment,
    Measurement,
    MeasurementContext,
    Bioreplicate,
    Study,
)

PLOTLY_TEMPLATE = 'plotly_white'


class StudyChartForm:
    def __init__(self, db_session, study):
        self.db_session = db_session
        self.study      = study

        self.measurement_context_ids = []
        self.measurement_contexts    = []

        self.left_axis_ids  = set()
        self.right_axis_ids = set()

    def build_chart(self, args):
        chart = Chart()
        self._extract_args(args)

        self.measurement_contexts = self.db_session.scalars(
            sql.select(MeasurementContext)
            .where(MeasurementContext.id.in_(self.measurement_context_ids))
        ).all()

        for measurement_context in self.measurement_contexts:
            df = self.get_df(measurement_context.id)

            subject      = measurement_context.get_subject(self.db_session)
            technique    = measurement_context.technique
            bioreplicate = measurement_context.bioreplicate
            compartment  = measurement_context.compartment

            if technique.subjectType == 'metabolite':
                label_parts = [f"<b>{subject.name}</b>"]
            else:
                label_parts = [f"<b>{technique.short_name}</b>"]
            if technique.units:
                label_parts.append(f"(<b>{technique.units}</b>)")

            if technique.subjectType == 'bioreplicate':
                label_parts.append('of the')
                label_parts.append(f"<b>{subject.name}<sub>{compartment.name}</sub></b>")
                label_parts.append('community')
            elif technique.subjectType == 'metabolite':
                label_parts.append('in')
                label_parts.append(f"<b>{bioreplicate.name}<sub>{compartment.name}</sub></b>")
            else:
                label_parts.append('of')
                label_parts.append(f"<b>{subject.name}</b>")
                label_parts.append('in')
                label_parts.append(f"{bioreplicate.name}<sub>{compartment.name}</sub>")

            label = ' '.join(label_parts)
            axis = 'right' if measurement_context.id in self.right_axis_ids else 'left'

            chart.add_df(df, label=label, axis=axis)

        return chart

    def _extract_args(self, args):
        self.measurement_context_ids = []
        self.left_axis_ids = set()
        self.right_axis_ids = set()

        for arg, value in args.items():
            if arg.startswith('measurementContext|'):
                context_id = int(arg.removeprefix('measurementContext|'))
                self.measurement_context_ids.append(context_id)
                self.left_axis_ids.add(context_id)

            elif arg.startswith('axis|'):
                context_id = int(arg.removeprefix('axis|'))

                if value == 'left':
                    # Left axis by default
                    pass
                elif value == 'right':
                    self.left_axis_ids.discard(context_id)
                    self.right_axis_ids.add(context_id)
                else:
                    raise ValueError(f"Unexpected axis: {value}")

    def get_df(self, measurement_context_id):
        query = (
            sql.select(
                Measurement.timeInHours.label("time"),
                Measurement.value,
                Measurement.std,
            )
            .select_from(Measurement)
            .where(
                Measurement.contextId == measurement_context_id,
                Measurement.value.is_not(None),
            )
            .order_by(Measurement.timeInSeconds)
        )

        return execute_into_df(self.db_session, query)

    def _transform_values(self, df, *, log=False):
        value_label = 'Cells/mL'
        value_std = None

        if log:
            value_label = 'log(Cells)/mL'

            # If we have 0 values, we'll get NaNs, which is okay for
            # rendering purposes, so we ignore the error:
            with np.errstate(divide='ignore'):
                df['value'] = np.log10(df['value'])
        else:
            value_std = df['std']

            if value_std.isnull().all():
                # STD values were blank, don't draw error bars
                value_std = None

        return value_label, value_std

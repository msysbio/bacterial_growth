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

    def build_chart(self, technique_id, args):
        chart = Chart()

        measurement_context_ids = self._extract_args(args)

        for measurement_context_id in measurement_context_ids:
            df = self.get_df(measurement_context_id)
            chart.add_df(f"MC {measurement_context_id}", df)

        return chart

    def _extract_args(self, args):
        measurement_context_ids = []

        for arg in args:
            if arg.startswith('measurementContext|'):
                context_id = int(arg.removeprefix('measurementContext|'))
                measurement_context_ids.append(context_id)

        return measurement_context_ids

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

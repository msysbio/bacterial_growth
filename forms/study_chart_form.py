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

        self.cell_count_units = 'Cells/mL'
        self.cfu_count_units  = 'CFUs/mL'
        self.metabolite_units = 'mM'

    def build_chart(self, args, width):
        self._extract_args(args)

        chart = Chart(
            time_units=self.study.timeUnits,
            cell_count_units=self.cell_count_units,
            cfu_count_units=self.cfu_count_units,
            metabolite_units=self.metabolite_units,
            log_left=self.log_left,
            log_right=self.log_right,
            width=width,
        )

        self.measurement_contexts = self.db_session.scalars(
            sql.select(MeasurementContext)
            .where(MeasurementContext.id.in_(self.measurement_context_ids))
        ).all()

        for measurement_context in self.measurement_contexts:
            technique = measurement_context.technique

            if measurement_context.id in self.right_axis_ids:
                axis = 'right'
                log_transform = self.log_right
            else:
                axis = 'left'
                log_transform = self.log_left

            df = self.get_df(measurement_context.id)
            if log_transform:
                self._apply_log_transform(df)

            label = measurement_context.get_chart_label(self.db_session)

            if technique.subjectType == 'metabolite':
                metabolite_mass = subject.averageMass
            else:
                metabolite_mass = None

            chart.add_df(
                df,
                units=technique.units,
                label=label,
                axis=axis,
                metabolite_mass=metabolite_mass,
            )

        return chart

    def _extract_args(self, args):
        self.measurement_context_ids = []

        self.left_axis_ids  = set()
        self.right_axis_ids = set()

        self.log_left  = False
        self.log_right = False

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

            elif arg == 'log-left':
                self.log_left = True
            elif arg == 'log-right':
                self.log_right = True

            elif arg == 'cellCountUnits':
                self.cell_count_units = value
            elif arg == 'cfuCountUnits':
                self.cfu_count_units = value
            elif arg == 'metaboliteUnits':
                self.metabolite_units = value

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

    def _apply_log_transform(self, df):
        if not df['std'].isnull().all():
            # Transform std values by summing them and transforming the results:
            with np.errstate(divide='ignore'):
                upper_log = np.log(df['value'] + df['std'])
                lower_log = np.log(df['value'] - df['std'])
                df['std'] = upper_log - lower_log

        with np.errstate(divide='ignore'):
            df['value'] = np.log(df['value'])

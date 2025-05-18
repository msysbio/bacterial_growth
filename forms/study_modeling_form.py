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


class StudyModelingForm:
    def __init__(self, db_session, study):
        self.db_session = db_session
        self.study      = study

        self.modeling_type = None
        self.log_transform = False

    def build_chart(self, args, width):
        self._extract_args(args)

        chart = Chart(
            time_units=self.study.timeUnits,
            width=width,
        )

        self.measurement_contexts = self.db_session.scalars(
            sql.select(MeasurementContext)
            .where(MeasurementContext.id.in_(self.measurement_context_ids))
        ).all()

        for measurement_context in self.measurement_contexts:
            df = measurement_context.get_df(self.db_session)
            if self.log_transform:
                self._apply_log_transform(df)

            subject      = measurement_context.get_subject(self.db_session)
            technique    = measurement_context.technique
            bioreplicate = measurement_context.bioreplicate
            compartment  = measurement_context.compartment

            label = f"Model: {self.modeling_type}"

            if technique.subjectType == 'metabolite':
                metabolite_mass = subject.averageMass
            else:
                metabolite_mass = None

            chart.add_df(
                df,
                units=technique.units,
                label=label,
            )

        return chart

    def _extract_args(self, args):
        self.modeling_type = args['modelingType']
        self.measurement_context_ids = []

        for arg, value in args.items():
            if arg.startswith('measurementContext|'):
                context_id = int(arg.removeprefix('measurementContext|'))
                self.measurement_context_ids.append(context_id)

    # TODO extract to Chart?
    def _apply_log_transform(self, df):
        if not df['std'].isnull().all():
            # Transform std values by summing them and transforming the results:
            with np.errstate(divide='ignore'):
                upper_log = np.log(df['value'] + df['std'])
                lower_log = np.log(df['value'] - df['std'])
                df['std'] = upper_log - lower_log

        with np.errstate(divide='ignore'):
            df['value'] = np.log(df['value'])

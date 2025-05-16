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

        selected_bioreplicates, include_average, apply_log = self._extract_args(args)
        bioreplicate_uuids = [b.id for b in selected_bioreplicates]

        # df = self.get_df(bioreplicate_uuids, technique, 'bioreplicate')
        # if include_average:
        #     average_df = self.get_average_df(technique, 'bioreplicate')
        #     df         = pd.concat((df, average_df))

        for bioreplicate_uuid in bioreplicate_uuids:
            df = self.get_df([bioreplicate_uuid], technique_id, 'bioreplicate')
            chart.add_df(f"Bioreplicate {bioreplicate_uuid}", df)

        return chart

    def _extract_args(self, args):
        bioreplicate_uuids = []
        include_average = False
        apply_log = [False for _ in args]

        for arg in args:
            if arg.endswith(':_average'):
                include_average = True
            elif arg.startswith('bioreplicate:'):
                bioreplicate_uuids.append(arg[len('bioreplicate:'):])
            elif arg.startswith('apply_log:'):
                index = int(arg[len('apply_log:'):])
                apply_log[index] = True

        selected_bioreplicates = self.db_session.scalars(
            sql.select(Bioreplicate)
            .where(Bioreplicate.id.in_(bioreplicate_uuids))
        ).all()

        return selected_bioreplicates, include_average, apply_log

    def get_df(self, bioreplicate_uuids, technique_id, subject_type):
        subjectName, subjectJoin = MeasurementContext.subject_join(subject_type)

        query = (
            sql.select(
                Measurement.timeInHours.label("time"),
                Measurement.value,
                Measurement.std,
                subjectName,
            )
            .select_from(Measurement)
            .join(MeasurementContext)
            .join(*subjectJoin)
            .where(
                MeasurementContext.bioreplicateId.in_(bioreplicate_uuids),
                MeasurementContext.techniqueId == technique_id,
                MeasurementContext.subjectType == subject_type,
                Measurement.contextId == MeasurementContext.id,
                Measurement.value.is_not(None),
            )
            .order_by('subjectName', Measurement.timeInSeconds)
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

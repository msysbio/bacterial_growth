import plotly.express as px
import numpy as np
import pandas as pd
import sqlalchemy as sql
from sqlalchemy.sql.expression import literal_column

from db import get_connection, get_session
from lib.db import execute_into_df
from models import (
    Experiment,
    Measurement,
    Bioreplicate,
)

PLOTLY_TEMPLATE = 'plotly_white'


class ExperimentChartForm:
    def __init__(self, experiment):
        self.experiment = experiment

        with get_connection() as db_conn:
            self.available_techniques = db_conn.execute(
                sql.select(Measurement.technique)
                .join(Bioreplicate)
                .distinct()
                .where(Bioreplicate.experimentId == self.experiment.id)
                .order_by(Measurement.technique)
            ).scalars()

    def generate_growth_figures(self, technique, args):
        selected_bioreplicates, include_average, _ = self._extract_args(args)
        bioreplicate_uuids = [b.id for b in selected_bioreplicates]

        df = self.get_df(bioreplicate_uuids, technique, 'bioreplicate')
        if include_average:
            average_df = self.get_average_df(technique, 'bioreplicate')
            df         = pd.concat((df, average_df))

        fig = self._render_figure(
            df,
            title=f'{technique} Plot for Experiment: {self.experiment.name} per Biological replicate',
            labels={
                'time': 'Hours',
                'value': 'Cells/mL',
                'subjectName': 'Bioreplicate',
            },
        )

        return [fig]

    def generate_reads_figures(self, technique, args):
        selected_bioreplicates, include_average, apply_log = self._extract_args(args)

        if technique == '16S rRNA-seq':
            measurement_label = '16S reads'
        else:
            measurement_label = 'FC Counts'

        figs = []
        for index, bioreplicate in enumerate(selected_bioreplicates):
            df = self.get_df([bioreplicate.id], technique, 'strain')

            value_label, value_std = self._transform_values(df, log=apply_log[index])

            figs.append(self._render_figure(
                df,
                # TODO (2025-03-03) STD should be handled consistently with apply_log
                error_y=value_std,
                title=f'{measurement_label}: {bioreplicate.name} per Microbial Strain',
                labels={
                    'time': 'Hours',
                    'value': value_label,
                    'subjectName': 'Species',
                },
            ))

        if include_average:
            df = self.get_average_df(technique, 'strain')

            # Last "apply_log" entry (TODO hacky):
            value_label, value_std = self._transform_values(df, log=apply_log[-1])

            figs.append(self._render_figure(
                df,
                # TODO (2025-03-03) STD should be handled consistently with apply_log
                error_y=value_std,
                title=f'{measurement_label}: Average {self.experiment.name} per Microbial Strain',
                labels={
                    'time': 'Hours',
                    'value': value_label,
                    'subjectName': 'Species',
                },
            ))

        return figs

    def generate_metabolite_figures(self, technique, args):
        selected_bioreplicates, include_average, _ = self._extract_args(args)

        figs = []
        for bioreplicate in selected_bioreplicates:
            df = self.get_df([bioreplicate.id], technique, 'metabolite')

            figs.append(self._render_figure(
                df,
                title=f'Metabolite Concentrations: {bioreplicate.name} per Metabolite',
                labels={
                    'time': 'Hours',
                    'value': 'mM',
                    'subjectName': 'Metabolite',
                },
            ))

        if include_average:
            df = self.get_average_df(technique, 'metabolite')

            # TODO (2025-03-05) Instead of hardcoding, add units

            figs.append(self._render_figure(
                df,
                error_y=df['std'],
                title=f'Average metabolite concentrations for: {self.experiment.name}',
                labels={
                    'time': 'Hours',
                    'value': 'mM',
                    'subjectName': 'Metabolite',
                },
            ))

        return figs

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

        with get_session() as db_session:
            selected_bioreplicates = db_session.scalars(
                sql.select(Bioreplicate)
                .where(Bioreplicate.id.in_(bioreplicate_uuids))
            ).all()

        return selected_bioreplicates, include_average, apply_log

    def get_df(self, bioreplicate_uuids, technique, subject_type):
        subjectName, subjectJoin = Measurement.subject_join(subject_type)

        query = (
            sql.select(
                Measurement.timeInHours.label("time"),
                Measurement.value,
                Measurement.std,
                subjectName,
            )
            .join(Bioreplicate)
            .join(*subjectJoin)
            .where(
                Measurement.bioreplicateUniqueId.in_(bioreplicate_uuids),
                Measurement.technique == technique,
                Measurement.subjectType == subject_type,
                Measurement.value.is_not(None),
            )
            .order_by('subjectName', Measurement.timeInSeconds)
        )

        with get_connection() as db_conn:
            return execute_into_df(db_conn, query)

    def get_average_df(self, technique, subject_type):
        if subject_type == 'bioreplicate':
            subjectName = literal_column('CONCAT("Average ", Experiments.name)').label('subjectName')
            subjectJoin = None
        else:
            subjectName, subjectJoin = Measurement.subject_join(subject_type)

        query = (
            sql.select(
                Measurement.timeInHours.label("time"),
                sql.func.avg(Measurement.value).label("value"),
                sql.func.stddev(Measurement.value).label("std"),
                subjectName,
            )
            .join(Bioreplicate)
            .join(Experiment)
            .where(
                Measurement.technique == technique,
                Measurement.subjectType == subject_type,
                Experiment.id == self.experiment.id,
            )
            .group_by(Measurement.timeInSeconds, subjectName)
            .order_by(sql.text('subjectName'), Measurement.timeInSeconds)
        )

        if subjectJoin is not None:
            query = query.join(*subjectJoin)

        with get_connection() as db_conn:
            return execute_into_df(db_conn, query)

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

    def _render_figure(self, df, **params):
        return px.line(
            df,
            x='time',
            y='value',
            color='subjectName',
            template=PLOTLY_TEMPLATE,
            markers=True,
            **params
        )

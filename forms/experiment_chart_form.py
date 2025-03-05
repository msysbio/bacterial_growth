import re

import plotly.express as px
import numpy as np
import pandas as pd
import sqlalchemy as sql
import sqlalchemy.dialects.mysql as mysql
from sqlalchemy.sql.expression import literal_column, literal

from db import get_connection, get_session
from models.experiment import Experiment
from models.measurement import Measurement
from models.metabolite import Metabolite
from models.strain import Strain
from models.bioreplicate import Bioreplicate

PLOTLY_TEMPLATE = 'plotly_white'


class ExperimentChartForm:
    def __init__(self, experiment):
        self.experiment = experiment

        with get_connection() as db_conn:
            self.available_techniques = db_conn.execute(
                sql.select(Measurement.technique)
                .join(Bioreplicate)
                .distinct()
                .where(Bioreplicate.experimentUniqueId == self.experiment.experimentUniqueId)
                .order_by(Measurement.technique)
            ).scalars()

    def generate_growth_figures(self, technique, args):
        selected_bioreplicates, include_average, _ = self.extract_args(args)
        bioreplicate_uuids = [b.bioreplicateUniqueId for b in selected_bioreplicates]

        df = self.get_df(bioreplicate_uuids, technique, 'bioreplicate')
        if include_average:
            average_df = self.get_average_df(technique, 'bioreplicate')
            print(average_df)
            df = pd.concat((df, average_df))

        fig = self._render_figure(
            df,
            title=f'{technique} Plot for Experiment: {self.experiment.experimentId} per Biological replicate',
            labels={
                'time': 'Hours',
                'value': 'Cells/mL',
                'subjectName': 'Bioreplicate',
            },
        )

        return [fig]

    def generate_reads_figures(self, technique, args):
        selected_bioreplicates, include_average, apply_log = self.extract_args(args)

        figs = []
        for index, bioreplicate in enumerate(selected_bioreplicates):
            df = self.get_df([bioreplicate.bioreplicateUniqueId], technique, 'strain')

            if technique == '16S rRNA-seq':
                title = f'16S reads: {bioreplicate.bioreplicateId} per Microbial Strain'
            else:
                title = f'FC Counts: {bioreplicate.bioreplicateId} per Microbial Strain'

            value_label = 'Cells/mL'
            value_std = None

            if apply_log[index]:
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

            figs.append(self._render_figure(
                df,
                # TODO (2025-03-03) STD should be handled consistently with apply_log
                error_y=value_std,
                title=title,
                labels={
                    'time': 'Hours',
                    'value': value_label,
                    'subjectName': 'Species',
                },
            ))

        if include_average:
            df = self.get_average_df(technique, 'strain')

            # Last "apply_log" entry (TODO hacky):
            if apply_log[-1]:
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

            if technique == '16S rRNA-seq':
                title = f'16S reads: Average {self.experiment.experimentId} per Microbial Strain'
            else:
                title = f'FC Counts: Average {self.experiment.experimentId} per Microbial Strain'

            figs.append(self._render_figure(
                df,
                # TODO (2025-03-03) STD should be handled consistently with apply_log
                error_y=value_std,
                title=title,
                labels={
                    'time': 'Hours',
                    'value': value_label,
                    'subjectName': 'Species',
                },
            ))

        return figs

    def generate_metabolite_figures(self, technique, args):
        selected_bioreplicates, include_average, _ = self.extract_args(args)

        figs = []
        for bioreplicate in selected_bioreplicates:
            df = self.get_df([bioreplicate.bioreplicateUniqueId], technique, 'metabolite')

            figs.append(self._render_figure(
                df,
                title=f'Metabolite Concentrations: {bioreplicate.bioreplicateId} per Metabolite',
                labels={
                    'time': 'Hours',
                    'value': 'mM',
                    'subjectName': 'Metabolite',
                },
            ))

        if include_average:
            df = self.get_average_df(technique, 'metabolite')
            print(df)

            figs.append(self._render_figure(
                df,
                error_y=df['std'],
                title=f'Average metabolite concentrations for: {self.experiment.experimentId}',
                labels={
                    'time': 'Hours',
                    'value': 'mM',
                    'subjectName': 'Metabolite',
                },
            ))


        return figs

    def extract_args(self, args):
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
                .where(Bioreplicate.bioreplicateUniqueId.in_(bioreplicate_uuids))
            ).all()

        return selected_bioreplicates, include_average, apply_log

    def get_df(self, bioreplicate_uuids, technique, subject_type):
        subjectName, subjectJoin = Measurement.subject_join(subject_type)

        query = (
            sql.select(
                (Measurement.timeInSeconds // 3600).label("time"),
                Measurement.absoluteValue.label("value"),
                Measurement.absoluteValueStd.label("std"),
                subjectName,
                Bioreplicate.bioreplicateId,
            )
            .join(Bioreplicate, Measurement.bioreplicateUniqueId == Bioreplicate.bioreplicateUniqueId)
            .join(*subjectJoin)
            .where(
                Measurement.bioreplicateUniqueId.in_(bioreplicate_uuids),
                Measurement.technique == technique,
                Measurement.subjectType == subject_type,
            )
            .order_by('subjectName', Measurement.timeInSeconds)
        )

        with get_connection() as db_conn:
            statement = query.compile(dialect=mysql.dialect())
            return pd.read_sql(statement, db_conn)

    def get_average_df(self, technique, subject_type):
        if subject_type == 'bioreplicate':
            subjectName = literal_column(f"'Average {self.experiment.experimentId}'").label('subjectName')
            subjectJoin = None
        else:
            subjectName, subjectJoin = Measurement.subject_join(subject_type)
            grouping = (Measurement.timeInSeconds, subjectName)

        query = (
            sql.select(
                (Measurement.timeInSeconds // 3600).label("time"),
                sql.func.avg(Measurement.absoluteValue).label("value"),
                sql.func.stddev(Measurement.absoluteValue).label("std"),
                subjectName,
                literal_column('CONCAT("Average ", Experiments.experimentId)').label("bioreplicateId"),
            )
            .join(Bioreplicate, Measurement.bioreplicateUniqueId == Bioreplicate.bioreplicateUniqueId)
            .join(Experiment, Bioreplicate.experimentUniqueId == Experiment.experimentUniqueId)
            .where(
                Measurement.technique == technique,
                Measurement.subjectType == subject_type,
                Experiment.experimentUniqueId == self.experiment.experimentUniqueId,
            )
            .group_by(Measurement.timeInSeconds, subjectName)
            .order_by(sql.text('subjectName'), Measurement.timeInSeconds)
        )

        if subjectJoin is not None:
            query = query.join(*subjectJoin)

        with get_connection() as db_conn:
            statement = query.compile(dialect=mysql.dialect())
            return pd.read_sql(statement, db_conn)

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

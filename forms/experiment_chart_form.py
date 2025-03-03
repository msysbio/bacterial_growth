import re

import plotly.express as px
import numpy as np
import pandas as pd
import sqlalchemy as sql
import sqlalchemy.dialects.mysql as mysql
from sqlalchemy.orm import aliased

from db import get_connection
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
        selected_bioreplicate_uuids, _ = self.extract_args(args)
        df = self.get_df(selected_bioreplicate_uuids, technique, 'bioreplicate')
        if len(df) == 0:
            continue

        fig = px.line(
            df,
            x='time',
            y='value',
            color='subjectName',
            title=f'{technique} Plot for Experiment: {self.experiment.experimentId} per Biological replicate',
            labels={
                'time': 'Hours',
                'value': 'Cells/mL',
                'subjectName': 'Bioreplicate',
            },
            template=PLOTLY_TEMPLATE,
            markers=True
        )

        return [fig]

    def generate_reads_figures(self, technique, args):
        selected_bioreplicate_uuids, apply_log = self.extract_args(args)

        figs = []
        for index, bioreplicate_uuid in enumerate(selected_bioreplicate_uuids):
            df = self.get_df([bioreplicate_uuid], technique, 'strain')
            if len(df) == 0:
                continue

            # TODO (2025-03-02) Hacky
            bioreplicate_id = df['bioreplicateId'].tolist()[0]

            if technique == '16S rRNA-seq':
                title = f'16S reads: {bioreplicate_id} per Microbial Strain'
            else:
                title = f'FC Counts: {bioreplicate_id} per Microbial Strain'

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

                if len(value_std) == 0:
                    # STD values were blank, don't draw error bars
                    value_std = None

            figs.append(px.line(
                df,
                x='time',
                y='value',
                color='subjectName',
                error_y=value_std,
                title=title,
                labels={
                    'time': 'Hours',
                    'value': value_label,
                    'subjectName': 'Species',
                },
                template=PLOTLY_TEMPLATE,
                markers=True
            ))

        return figs

    def generate_metabolite_figures(self, technique, args):
        selected_bioreplicate_uuids, _ = self.extract_args(args)

        figs = []
        for bioreplicate_uuid in selected_bioreplicate_uuids:
            df = self.get_df([bioreplicate_uuid], technique, 'metabolite')
            if len(df) == 0:
                continue

            # TODO (2025-03-02) Hacky
            bioreplicate_id = df['bioreplicateId'].tolist()[0]

            figs.append(px.line(
                df,
                x='time',
                y='value',
                color='subjectName',
                title=f'Metabolite Concentrations: {bioreplicate_id} per Metabolite',
                labels={
                    'time': 'Hours',
                    'value': 'mM',
                    'subjectName': 'Metabolite',
                },
                template=PLOTLY_TEMPLATE,
                markers=True
            ))

        return figs

    def extract_args(self, args):
        selected_bioreplicate_ids = []
        include_average = False
        apply_log = [False for _ in args]

        for arg in args:
            if arg.endswith(':_average'):
                include_average = True
            elif arg.startswith('bioreplicate:'):
                selected_bioreplicate_ids.append(arg[len('bioreplicate:'):])
            elif arg.startswith('apply_log:'):
                index = int(arg[len('apply_log:'):])
                apply_log[index] = True

        if include_average:
            selected_bioreplicate_ids.append(f"Average {self.experiment.experimentId}")

        return selected_bioreplicate_ids, apply_log

    def get_df(self, bioreplicate_uuids, technique, subject_type):
        if subject_type == 'metabolite':
            subjectName = Metabolite.metabo_name.label("subjectName")
            subjectJoin = (Metabolite, Measurement.subjectId == Metabolite.chebi_id)
        elif subject_type == 'strain':
            subjectName = Strain.memberName.label("subjectName")
            subjectJoin = (Strain, Measurement.subjectId == Strain.strainId)
        elif subject_type == 'bioreplicate':
            subjectName = Bioreplicate.bioreplicateId.label("subjectName")
            Subject = aliased(Bioreplicate)
            subjectJoin = (Subject, Measurement.subjectId == Subject.bioreplicateUniqueId)

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
        statement = query.compile(dialect=mysql.dialect())

        with get_connection() as db_conn:
            return pd.read_sql(statement, db_conn)

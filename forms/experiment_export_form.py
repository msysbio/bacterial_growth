import functools

import sqlalchemy as sql
from sqlalchemy.sql.expression import literal_column
import pandas as pd

from models import (
    Bioreplicate,
    Compartment,
    Experiment,
    Measurement,
)
from lib.db import execute_into_df

# TODO (2025-03-08) Tests
# TODO (2025-03-08) Benchmark, improve performance


class ExperimentExportForm:
    def __init__(self, db_session, args):
        self.db_session = db_session

        self.bioreplicate_uuids = []
        self.averaged_experiments = set()
        self._extract_bioreplicate_args(args)

        self.csv_separator = ','
        self._extract_csv_args(args)

        self.experiments = self.db_session.scalars(
            sql.select(Experiment)
            .join(Bioreplicate)
            .where(
                sql.or_(
                    Bioreplicate.id.in_(self.bioreplicate_uuids),
                    Experiment.id.in_(self.averaged_experiments),
                ),
            )
            .group_by(Experiment.id)
        ).all()

    def get_experiment_data(self):
        experiment_data = {}
        get_subject = functools.cache(Measurement.get_subject)

        for experiment in self.experiments:
            measurement_dfs = []
            measurement_targets = {
                'bioreplicate': set(),
                'metabolite':   set(),
                'strain':       set(),
            }

            # Collect targets for each column of measurements:
            for measurement in experiment.measurements:
                if measurement.subjectType == 'bioreplicate':
                    measurement_targets['bioreplicate'].add((
                        measurement.technique,
                        measurement.unit,
                    ))
                else:
                    subject = get_subject(self.db_session, measurement.subjectId, measurement.subjectType)
                    measurement_targets[measurement.subjectType].add((
                        subject,
                        measurement.technique,
                        measurement.unit,
                    ))

            # Strain-level measurements:
            for (subject, technique, unit) in sorted(measurement_targets['strain']):
                if technique == '16S rRNA-seq':
                    value_label = f"{subject.name} reads"
                elif technique == 'FC counts per species':
                    value_label = f"{subject.name} counts"
                elif technique == 'plates':
                    value_label = f"{subject.name} plate counts"
                else:
                    raise ValueError(f"Unknown technique: {technique}")

                condition = (
                    Measurement.subjectType == 'strain',
                    Measurement.subjectId == subject.id,
                    Measurement.technique == technique,
                )

                query = self._base_bioreplicate_query(experiment, value_label).where(*condition)
                measurement_dfs.append(execute_into_df(self.db_session, query))

                if str(experiment.id) in self.averaged_experiments:
                    query = self._base_average_query(experiment, value_label).where(*condition)
                    average_df = execute_into_df(self.db_session, query)
                    measurement_dfs[-1] = pd.concat((measurement_dfs[-1], average_df))

            # Bioreplicate-level measurements:
            for (technique, unit) in measurement_targets['bioreplicate']:
                if unit is None:
                    value_label = technique
                else:
                    value_label = f"{technique} ({unit})"

                condition = (
                    Measurement.subjectType == 'bioreplicate',
                    Measurement.technique == technique,
                )

                query = self._base_bioreplicate_query(experiment, value_label).where(*condition)
                measurement_dfs.append(execute_into_df(self.db_session, query))

                if str(experiment.id) in self.averaged_experiments:
                    query = self._base_average_query(experiment, value_label).where(*condition)
                    average_df = execute_into_df(self.db_session, query)
                    measurement_dfs[-1] = pd.concat((measurement_dfs[-1], average_df))

            # Metabolite measurements:
            for (subject, _, unit) in sorted(measurement_targets['metabolite']):
                value_label = f"{subject.name} ({unit})"
                condition = (
                    Measurement.subjectType == 'metabolite',
                    Measurement.subjectId == subject.id,
                )

                query = self._base_bioreplicate_query(experiment, value_label).where(*condition)
                measurement_dfs.append(execute_into_df(self.db_session, query))

                if str(experiment.id) in self.averaged_experiments:
                    query = self._base_average_query(experiment, value_label).where(*condition)
                    average_df = execute_into_df(self.db_session, query)
                    measurement_dfs[-1] = pd.concat((measurement_dfs[-1], average_df))

            if len(measurement_dfs) == 0:
                continue

            # Join separate dataframes, one per column
            experiment_df = measurement_dfs[0]
            for df in measurement_dfs[1:]:
                experiment_df = experiment_df.merge(
                    df,
                    how='left',
                    on=['Time (hours)', 'Biological Replicate', 'Compartment'],
                    validate='one_to_one',
                    suffixes=(None, None),
                )

            if len(experiment_df) == 0:
                continue

            experiment_data[experiment] = experiment_df

        return experiment_data

    def _base_bioreplicate_query(self, experiment, value_label):
        return (
            sql.select(
                Measurement.timeInHours.label("Time (hours)"),
                Bioreplicate.name.label("Biological Replicate"),
                Compartment.name.label("Compartment"),
                Measurement.value.label(value_label),
            )
            .join(Bioreplicate)
            .join(Compartment)
            .join(Experiment)
            .where(
                Experiment.id == experiment.id,
                Bioreplicate.id.in_(self.bioreplicate_uuids),
            )
            .order_by(
                Bioreplicate.name,
                Compartment.name,
                Measurement.timeInSeconds,
            )
        )

    def _base_average_query(self, experiment, value_label):
        return (
            sql.select(
                Measurement.timeInHours.label("Time (hours)"),
                literal_column(f"'Average {experiment.name}'").label("Biological Replicate ID"),
                sql.func.avg(Measurement.value).label(value_label),
            )
            .join(Bioreplicate)
            .join(Experiment)
            .where(Experiment.id == experiment.id)
            .group_by(Measurement.timeInSeconds)
            .order_by(Measurement.timeInSeconds)
        )

    def _extract_bioreplicate_args(self, args):
        for arg in args.getlist('bioreplicates'):
            if arg.startswith('_average:'):
                experiment_uuid = arg.removeprefix('_average:')
                self.averaged_experiments.add(experiment_uuid)
            else:
                self.bioreplicate_uuids.append(arg)

    def _extract_csv_args(self, args):
        delimiter = args.get('delimiter', 'comma')

        if delimiter == 'comma':
            self.sep = ','
        elif delimiter == 'tab':
            self.sep = '\t'
        elif delimiter == 'custom':
            self.sep = args.get('custom_delimiter', '|')
            if self.sep == '':
                self.sep = ' '
        else:
            raise Exception(f"Unknown delimiter requested: {delimiter}")

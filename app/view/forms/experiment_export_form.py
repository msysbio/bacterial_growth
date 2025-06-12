import sqlalchemy as sql

from app.model.orm import (
    Bioreplicate,
    Compartment,
    Experiment,
    Measurement,
    MeasurementContext,
)
from app.model.lib.db import execute_into_df

# TODO (2025-03-08) Tests
# TODO (2025-03-08) Benchmark, improve performance


class ExperimentExportForm:
    def __init__(self, db_session, args):
        self.db_session = db_session

        self.bioreplicate_uuids = []
        self._extract_bioreplicate_args(args)

        self.csv_separator = ','
        self._extract_csv_args(args)

        self.experiments = self.db_session.scalars(
            sql.select(Experiment)
            .join(Bioreplicate)
            .where(Bioreplicate.id.in_(self.bioreplicate_uuids))
            .group_by(Experiment.id)
        ).all()

    def get_experiment_data(self):
        experiment_data = {}

        for experiment in self.experiments:
            measurement_dfs = []
            measurement_targets = {
                'bioreplicate': set(),
                'metabolite':   set(),
                'strain':       set(),
            }

            # Collect targets for each column of measurements:
            for measurement_context in experiment.measurementContexts:
                if measurement_context.subjectType == 'bioreplicate':
                    measurement_targets['bioreplicate'].add(measurement_context.technique)
                else:
                    subject = measurement_context.get_subject(self.db_session)
                    measurement_targets[measurement_context.subjectType].add((
                        subject,
                        measurement_context.technique,
                    ))

            # Strain-level measurements:
            for (subject, technique) in sorted(measurement_targets['strain']):
                if technique.type == '16s':
                    value_label = f"{subject.name} reads"
                elif technique.type == 'fc':
                    value_label = f"{subject.name} counts"
                elif technique.type == 'plates':
                    value_label = f"{subject.name} plate counts"
                else:
                    raise ValueError(f"Unknown technique type: {technique.type}")

                condition = (
                    MeasurementContext.subjectType == 'strain',
                    MeasurementContext.subjectId == subject.id,
                    MeasurementContext.techniqueId == technique.id,
                )

                query = self._base_bioreplicate_query(experiment, value_label).where(*condition)
                measurement_dfs.append(execute_into_df(self.db_session, query))

            # Bioreplicate-level measurements:
            for technique in measurement_targets['bioreplicate']:
                if technique.units is None:
                    value_label = technique
                else:
                    value_label = f"{technique.short_name} ({technique.units})"

                condition = (
                    MeasurementContext.subjectType == 'bioreplicate',
                    MeasurementContext.techniqueId == technique.id,
                )

                query = self._base_bioreplicate_query(experiment, value_label).where(*condition)
                measurement_dfs.append(execute_into_df(self.db_session, query))

            # Metabolite measurements:
            for (subject, technique) in sorted(measurement_targets['metabolite']):
                value_label = f"{subject.name} ({technique.units})"
                condition = (
                    MeasurementContext.subjectType == 'metabolite',
                    MeasurementContext.subjectId == subject.chebiId,
                )

                query = self._base_bioreplicate_query(experiment, value_label).where(*condition)
                measurement_dfs.append(execute_into_df(self.db_session, query))

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
            .select_from(Measurement)
            .join(MeasurementContext)
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

    def _extract_bioreplicate_args(self, args):
        for arg in args.getlist('bioreplicates'):
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

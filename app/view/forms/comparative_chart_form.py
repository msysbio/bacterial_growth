import sqlalchemy as sql

from app.model.lib.db import execute_into_df
from app.model.lib.chart import Chart
from app.model.lib.log_transform import apply_log_transform
from app.model.orm import (
    Measurement,
    MeasurementContext,
)


class ComparativeChartForm:
    def __init__(self, db_session, time_units, left_axis_ids=[], right_axis_ids=[]):
        self.db_session = db_session
        self.time_units = time_units

        self.left_axis_ids  = set(left_axis_ids)
        self.right_axis_ids = set(right_axis_ids)

        self.measurement_context_ids = list(self.left_axis_ids) + list(self.right_axis_ids)
        self.measurement_contexts    = []

        self.cell_count_units = 'Cells/mL'
        self.cfu_count_units  = 'CFUs/mL'
        self.metabolite_units = 'mM'

    def build_chart(self, args, width, legend_position='top', clamp_x_data=False):
        self._extract_args(args)

        chart = Chart(
            time_units=self.time_units,
            cell_count_units=self.cell_count_units,
            cfu_count_units=self.cfu_count_units,
            metabolite_units=self.metabolite_units,
            log_left=self.log_left,
            log_right=self.log_right,
            width=width,
            legend_position=legend_position,
            clamp_x_data=clamp_x_data,
        )

        self.measurement_contexts = self.db_session.scalars(
            sql.select(MeasurementContext)
            .where(MeasurementContext.id.in_(self.measurement_context_ids))
        ).all()

        for measurement_context in self.measurement_contexts:
            technique = measurement_context.technique
            subject = measurement_context.get_subject(self.db_session)

            if measurement_context.id in self.right_axis_ids:
                axis = 'right'
                log_transform = self.log_right
            else:
                axis = 'left'
                log_transform = self.log_left

            df = self.get_df(measurement_context.id)
            if log_transform:
                apply_log_transform(df)

            label = measurement_context.get_chart_label(self.db_session)

            if technique.subjectType == 'metabolite':
                metabolite_mass = subject.averageMass
            else:
                metabolite_mass = None

            if technique.units == '':
                units = technique.short_name
            else:
                units = technique.units

            chart.add_df(
                df,
                units=units,
                label=label,
                axis=axis,
                metabolite_mass=metabolite_mass,
            )

        return chart

    @property
    def permalink_query(self):
        left_axis_part  = ','.join([str(i) for i in self.left_axis_ids])
        right_axis_part = ','.join([str(i) for i in self.right_axis_ids])

        return f"l={left_axis_part}&r={right_axis_part}"

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

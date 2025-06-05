import math

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from app.model.lib.conversion import convert_measurement_units

PLOTLY_TEMPLATE = 'plotly_white'

CELL_COUNT_UNITS = ('Cells/mL', 'Cells/μL')
CFU_COUNT_UNITS  = ('CFUs/mL', 'CFUs/μL')
METABOLITE_UNITS = ('mM', 'μM', 'nM', 'pM', 'g/L')


class Chart:
    def __init__(
        self,
        time_units,
        cell_count_units='Cells/mL',
        cfu_count_units='CFUs/mL',
        metabolite_units='mM',
        log_left=False,
        log_right=False,
        width=None,
        title=None,
        legend_position='top',
        clamp_x_data=False,
    ):
        self.time_units       = time_units
        self.cell_count_units = cell_count_units
        self.cfu_count_units  = cfu_count_units
        self.metabolite_units = metabolite_units
        self.width            = width
        self.title            = title
        self.legend_position  = legend_position
        self.clamp_x_data     = clamp_x_data

        self.log_left  = log_left
        self.log_right = log_right

        self.data_left  = []
        self.data_right = []

        self.mixed_units_left  = False
        self.mixed_units_right = False

        self.model_df_indices = []

    def add_df(self, df, *, units, label=None, axis='left', metabolite_mass=None):
        entry = (df, units, label, metabolite_mass)

        if axis == 'left':
            self.data_left.append(entry)
        elif axis == 'right':
            self.data_right.append(entry)
        else:
            raise ValueError(f"Unexpected axis: {axis}")

    def add_model_df(self, df, *, units, label=None, axis='left'):
        self.model_df_indices.append(len(self.data_left) + len(self.data_right))
        entry = (df, units, label, None)

        if axis == 'left':
            self.data_left.append(entry)
        elif axis == 'right':
            self.data_right.append(entry)
        else:
            raise ValueError(f"Unexpected axis: {axis}")

    def to_html(self):
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        converted_data_left,  left_units_label  = self._convert_units(self.data_left)
        converted_data_right, right_units_label = self._convert_units(self.data_right)

        if left_units_label == '[mixed units]':
            self.mixed_units_left = True
        if right_units_label == '[mixed units]':
            self.mixed_units_right = True

        if self.log_left:
            left_units_label = f"ln({left_units_label})"
        if self.log_right:
            right_units_label = f"ln({right_units_label})"

        for (df, label) in converted_data_left:
            scatter_params = self._get_scatter_params(df, label)
            fig.add_trace(go.Scatter(**scatter_params), secondary_y=False)

        for (df, label) in converted_data_right:
            scatter_params = self._get_scatter_params(df, label)
            scatter_params = dict(**scatter_params, line={'dash': 'dot'})

            fig.add_trace(go.Scatter(**scatter_params), secondary_y=True)

        fig.update_yaxes(title_text=left_units_label,  secondary_y=False)
        fig.update_yaxes(title_text=right_units_label, secondary_y=True)

        if self.title:
            title = dict(text=self.title)
        else:
            title = dict(x=0)

        if self.legend_position == 'top':
            legend = dict(yanchor="bottom", y=1, xanchor="left", x=0)
        else:
            legend = None

        xaxis_range = self._calculate_x_range(converted_data_left + converted_data_right)
        yaxis_range = self._calculate_y_range(converted_data_left)

        fig.update_layout(
            template=PLOTLY_TEMPLATE,
            margin=dict(l=0, r=0, t=60, b=40),
            title=title,
            hovermode='x unified',
            legend=legend,
            xaxis_range=xaxis_range,
            yaxis_range=yaxis_range,
            yaxis=dict(
                exponentformat="power",
            ),
            xaxis=dict(
                title=dict(text=f"Time ({self.time_units})"),
            )
        )

        return fig.to_html(
            full_html=False,
            include_plotlyjs=False,
            default_width=(f"{self.width}px" if self.width is not None else None)
        )

    def _convert_units(self, data):
        if len(data) == 0:
            return [], None

        converted_units = set()
        converted_data = [(df, label) for (df, _, label, _) in data]

        for (df, units, label, metabolite_mass) in data:
            if units in CELL_COUNT_UNITS:
                result_units = self._convert_df_units(df, units, self.cell_count_units)
                converted_units.add(result_units)
            elif units in CFU_COUNT_UNITS:
                result_units = self._convert_df_units(df, units, self.cfu_count_units)
                converted_units.add(result_units)
            elif units in METABOLITE_UNITS:
                result_units = self._convert_df_units(df, units, self.metabolite_units, metabolite_mass)
                converted_units.add(result_units)
            else:
                converted_units.add(units)

        if len(converted_units) > 1 or len(converted_data) == 0:
            return converted_data, '[mixed units]'

        return converted_data, tuple(converted_units)[0]

    def _get_scatter_params(self, df, label):
        if 'std' in df:
            if df['std'].isnull().all():
                # STD values were blank, don't draw error bars
                error_y = None
            else:
                error_y = go.scatter.ErrorY(array=df['std'])
        else:
            error_y = None

        return dict(
            x=df['time'],
            y=df['value'],
            name=label,
            error_y=error_y,
        )

    def _convert_df_units(self, df, source_units, target_units, metabolite_mass=None):
        new_value = convert_measurement_units(
            df['value'],
            source_units,
            target_units,
            mass=metabolite_mass,
        )

        if new_value is not None:
            df['value'] = new_value
            if 'std' in df:
                df['std'] = convert_measurement_units(
                    df['std'],
                    source_units,
                    target_units,
                    mass=metabolite_mass,
                )
            return target_units
        else:
            return source_units

    def _calculate_x_range(self, data):
        if not self.clamp_x_data:
            return None

        # With multiple charts, fit the x-axis of the shortest one:
        global_max_x = math.inf
        global_min_x = 0

        for (i, (df, _)) in enumerate(data):
            max_x = df['time'].max() + 10
            min_x = df['time'].min() - 10

            if max_x < global_max_x:
                global_max_x = max_x
            if min_x > global_min_x:
                global_min_x = min_x

        return [global_min_x, global_max_x]

    def _calculate_y_range(self, data):
        if len(self.model_df_indices) == 0:
            return None

        # If we have added models, let's limit the y axis to avoid exponentials
        # shooting up
        # TODO (2025-05-20) Hack, only works on the left side
        global_max_y = 0
        global_min_y = math.inf

        for (i, (df, _)) in enumerate(data):
            if i in self.model_df_indices:
                continue

            std_y = df['value'].std()
            max_y = df['value'].max() + std_y / 2
            min_y = df['value'].min() - std_y / 2

            if max_y > global_max_y:
                global_max_y = max_y
            if min_y < global_min_y:
                global_min_y = min_y

        return [global_min_y, global_max_y]

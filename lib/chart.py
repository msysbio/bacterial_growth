import plotly.graph_objects as go
from plotly.subplots import make_subplots

from lib.conversion import convert_measurement_units

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
        legend_position='top'
    ):
        self.time_units       = time_units
        self.cell_count_units = cell_count_units
        self.cfu_count_units  = cfu_count_units
        self.metabolite_units = metabolite_units
        self.width            = width
        self.title            = title
        self.legend_position  = legend_position

        self.log_left  = log_left
        self.log_right = log_right

        self.data_left  = []
        self.data_right = []

        self.mixed_units_left  = False
        self.mixed_units_right = False

        self.has_model_df = False
        self.max_y = 0

    def add_df(self, df, *, units, label=None, axis='left', metabolite_mass=None):
        entry = (df, units, label, metabolite_mass)

        if axis == 'left':
            self.data_left.append(entry)
        elif axis == 'right':
            self.data_right.append(entry)
        else:
            raise ValueError(f"Unexpected axis: {axis}")

        std_y = df['value'].std()
        max_y = df['value'].max() + std_y / 2

        if max_y > self.max_y:
            self.max_y = max_y

    def add_model_df(self, df, *, units, label=None, axis='left'):
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

        if self.has_model_df:
            # We want to limit the size of the chart to avoid exponential
            # curves shooting out:
            # TODO: a bit of a hack, limits are set pre-unit-scaling
            yaxis_range=[0, self.max_y]
        else:
            yaxis_range=None

        fig.update_layout(
            template=PLOTLY_TEMPLATE,
            margin=dict(l=0, r=0, t=60, b=40),
            title=title,
            hovermode='x unified',
            legend=legend,
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
        if len(data) == 1:
            return converted_data, data[0][1]

        for (df, units, label, metabolite_mass) in data:
            if units in CELL_COUNT_UNITS:
                # Cell counts:
                new_value = convert_measurement_units(df['value'], units, self.cell_count_units)
                if new_value is not None:
                    df['value'] = new_value
                    if 'std' in df:
                        df['std'] = convert_measurement_units(df['std'], units, self.cell_count_units)
                    converted_units.add(self.cell_count_units)
                else:
                    converted_units.add(units)
            elif units in CFU_COUNT_UNITS:
                # CFU counts:
                new_value = convert_measurement_units(df['value'], units, self.cfu_count_units)
                if new_value is not None:
                    df['value'] = new_value
                    if 'std' in df:
                        df['std'] = convert_measurement_units(df['std'], units, self.cfu_count_units)
                    converted_units.add(self.cell_count_units)
                else:
                    converted_units.add(units)
            elif units in METABOLITE_UNITS:
                # Metabolites
                new_value = convert_measurement_units(df['value'], units, self.metabolite_units, mass=metabolite_mass)
                if new_value is not None:
                    df['value'] = new_value
                    if 'std' in df:
                        df['std'] = convert_measurement_units(df['std'], units, self.metabolite_units)
                    converted_units.add(self.metabolite_units)
                else:
                    converted_units.add(units)
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

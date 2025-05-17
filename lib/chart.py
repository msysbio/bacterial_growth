import plotly.graph_objects as go
from plotly.subplots import make_subplots

PLOTLY_TEMPLATE = 'plotly_white'


class Chart:
    def __init__(self, time_units):
        self.time_units = time_units

        self.data        = []
        self.units_left  = set()
        self.units_right = set()

        # TODO (2025-05-17) Set them via args or [multiple units]
        self.selected_left_units = None
        self.selected_right_units = None

    def add_df(self, df, units, label, axis):
        self.data.append((df, label, axis))

        if axis == 'left':
            self.units_left.add(units)
            self.selected_left_units = units
        elif axis == 'right':
            self.units_right.add(units)
            self.selected_right_units = units
        else:
            raise ValueError(f"Unexpected axis: {axis}")

    def to_html(self, width=None):
        # TODO (2025-05-15) value units
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        for (df, label, axis) in self.data:
            if df['std'].isnull().all():
                # STD values were blank, don't draw error bars
                error_y = None
            else:
                error_y = go.scatter.ErrorY(array=df['std'])

            scatter_params = dict(
                x=df['time'],
                y=df['value'],
                name=label,
                error_y=error_y,
            )

            if axis == 'left':
                secondary_y = False
            elif axis == 'right':
                scatter_params = dict(**scatter_params, line={'dash': 'dot'})
                secondary_y = True
            else:
                raise ValueError(f"Unexpected axis: {axis}")

            fig.add_trace(go.Scatter(**scatter_params), secondary_y=secondary_y)

        # TODO Pick units
        fig.update_yaxes(title_text=self.selected_left_units, secondary_y=False)
        fig.update_yaxes(title_text=self.selected_right_units, secondary_y=True)

        fig.update_layout(
            template=PLOTLY_TEMPLATE,
            margin=dict(l=0, r=0, t=60, b=40),
            title=dict(x=0),
            hovermode='x unified',
            legend=dict(
                yanchor="bottom",
                y=1,
                xanchor="left",
                x=0,
            ),
            xaxis=dict(
                title=dict(text=f"Time ({self.time_units})"),
                # TODO: doesn't work for some reason
                hoverformat=f"Time: %{{x}}{self.time_units}",
            )
        )

        return fig.to_html(
            full_html=False,
            include_plotlyjs=False,
            default_width=(f"{width}px" if width is not None else None)
        )

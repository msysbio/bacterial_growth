import plotly.graph_objects as go
from plotly.subplots import make_subplots

PLOTLY_TEMPLATE = 'plotly_white'


class Chart:
    def __init__(self):
        self.data = []

    def add_df(self, df, label, axis):
        self.data.append((label, axis, df))

    def to_html(self, width=None):
        # TODO (2025-05-15) time units
        # TODO (2025-05-15) value units
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        for (label, axis, df) in self.data:
            scatter_params = dict(x=df['time'], y=df['value'], name=label)

            if axis == 'left':
                secondary_y = False
            elif axis == 'right':
                scatter_params = dict(**scatter_params, line={'dash': 'dot'})
                secondary_y = True
            else:
                raise ValueError(f"Unexpected axis: {axis}")

            fig.add_trace(go.Scatter(**scatter_params), secondary_y=secondary_y)

        fig.update_layout(
            template=PLOTLY_TEMPLATE,
            margin=dict(l=0, r=0, t=60, b=40),
            title=dict(x=0),
            legend=dict(
                yanchor="bottom",
                y=1,
                xanchor="left",
                x=0,
            )
        )

        return fig.to_html(
            full_html=False,
            include_plotlyjs=False,
            default_width=(f"{width}px" if width is not None else None)
        )

import plotly.graph_objects as go
from plotly.subplots import make_subplots

PLOTLY_TEMPLATE = 'plotly_white'


class Chart:
    def __init__(self):
        self.data = []

    def add_df(self, name, df):
        self.data.append((name, df))

    def to_html(self, width=None):
        # TODO (2025-05-15) time units
        # TODO (2025-05-15) value units
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.update_layout(template=PLOTLY_TEMPLATE)

        for (name, df) in self.data:
            fig.add_trace(
                go.Scatter(x=df['time'], y=df['value'], name=name),
                secondary_y=False,
            )

        fig.update_layout(
            margin=dict(l=0, r=0, t=60, b=40),
            title=dict(x=0)
        )

        return fig.to_html(
            full_html=False,
            include_plotlyjs=False,
            default_width=(f"{width}px" if width is not None else None)
        )

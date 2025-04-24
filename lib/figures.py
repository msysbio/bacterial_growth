import plotly.graph_objects as go
from plotly.subplots import make_subplots

PLOTLY_TEMPLATE = 'plotly_white'


def make_figure_with_traces(data_dfs, **params):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.update_layout(template=PLOTLY_TEMPLATE)

    for df in data_dfs:
        fig.add_trace(
            go.Scatter(x=df['time'], y=df['value'], name=df['name'][0]),
            secondary_y=False,
        )

    return fig

def make_figure_with_secondary_axis(data, **params):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
    )

    for direction, df in data:
        if direction == 'left':
            fig.add_trace(
                go.Scatter(x=df['time'], y=df['value'], name=df['name'][0]),
                secondary_y=False,
            )
        elif direction == 'right':
            fig.add_trace(
                go.Scatter(x=df['time'], y=df['value'], name=df['name'][0], line={'dash': 'dot'}),
                secondary_y=True,
            )
        else:
            raise ValueError(f"Unexpected direction received: {direction}")

    return fig

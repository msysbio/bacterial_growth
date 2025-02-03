from plotly import graph_objects as go


# Plotly seems to have a bug where it needs to be initialized before it can be used properly.
#
# Community issue (from 2021!):
# https://community.plotly.com/t/valueerror-invalid-value-in-basedatatypes-py/55993
#
# Github fix:
# https://github.com/plotly/plotly.py/issues/3441#issuecomment-1271747147
#
def init_plotly():
    go.Figure(layout=dict(template='plotly'))

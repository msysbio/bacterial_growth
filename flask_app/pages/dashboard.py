import os

from flask import render_template, request
import sqlalchemy as sql
import plotly.express as px
import pandas as pd

from flask_app.db import get_connection
from flask_app.models.study_dfs import get_experiments


def dashboard_index_page():
    studyName = None
    studyId = request.args.get('studyId')
    experiments = []

    with get_connection() as conn:
        if studyId:
            query = "SELECT studyName FROM Study WHERE studyId = :studyId LIMIT 1"
            studyName = conn.execute(sql.text(query), { 'studyId': studyId }).scalar()

            df_experiments = get_experiments(studyId, conn)
            experiments = zip(
                df_experiments["experimentId"],
                df_experiments["experimentDescription"],
                [b_ids.split(',') for b_ids in df_experiments["bioreplicateIds"]]
            )

        return render_template(
            "pages/dashboard/index.html",
            studyId=studyId,
            studyName=studyName,
            experiments=experiments,
        )

def dashboard_chart_page():
    args = request.args.to_dict()

    studyId      = args.pop('studyId')
    experimentId = args.pop('experimentId')
    width        = args.pop('width')
    measurement  = args.pop('measurement')

    bioreplicate_ids = []
    include_average = False

    for arg in args:
        if arg.endswith(':_average'):
            include_average = True
        elif arg.startswith('bioreplicate:'):
            bioreplicate_ids.append(arg[len('bioreplicate:'):])

    df_growth, df_reads = get_chart_data(studyId)
    df_growth = df_growth[df_growth['Biological_Replicate_id'].isin(bioreplicate_ids)]

    if include_average:
        mean_df_specific_ids = df_growth.groupby('Time')[measurement].mean().reset_index()
        mean_df_specific_ids['Biological_Replicate_id'] = f"Average {experimentId}"
        df_growth = pd.concat([df_growth, mean_df_specific_ids], ignore_index=True)

    fig = px.line(
        df_growth,
        x='Time',
        y=measurement,
        color='Biological_Replicate_id',
        title=f'{measurement} Plot for Experiment: {experimentId} per Biological replicate',
        labels={'Time': 'Hours'},
        markers=True
    )

    result = fig.to_html(
        full_html=False,
        include_plotlyjs=False,
        default_width=f"{width}px",
    )

    return result

# TODO: Hack, reads static files
def get_chart_data(studyId):
    filepath = os.path.realpath(__file__)
    current_dir = os.path.dirname(filepath)
    root_dir = os.path.dirname(current_dir)
    relative_path_to_src = os.path.join(root_dir, '../src')

    path = relative_path_to_src + f"/Data/Growth/{studyId}"
    growth_file = path + f"/Growth_Metabolites.csv"
    reads_file = path + f"/Sequencing_Reads.csv"

    df_growth = pd.read_csv(growth_file)
    subset_columns = df_growth.columns.drop('Position')
    # Drop rows where all values are NaN
    df_growth = df_growth.dropna(subset=subset_columns, how='all')

    df_reads = pd.read_csv(reads_file)

    return (df_growth, df_reads)

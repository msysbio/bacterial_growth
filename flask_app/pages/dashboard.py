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
    available_growth_measurements = []

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

            df_growth, _ = get_chart_data(studyId)
            growth_keys = set(df_growth.keys())
            available_growth_measurements = [
                measurement
                for measurement in ['OD', 'Plate Counts', 'pH', 'FC']
                if measurement in growth_keys
            ]

        return render_template(
            "pages/dashboard/index.html",
            studyId=studyId,
            studyName=studyName,
            experiments=experiments,
            available_growth_measurements=available_growth_measurements
        )

def dashboard_chart_fragment():
    args = request.args.to_dict()

    studyId      = args.pop('studyId')
    experimentId = args.pop('experimentId')
    width        = args.pop('width')
    measurement  = args.pop('measurement')

    if measurement == 'Reads 16S rRNA Seq':
        # TODO (2024-08-28) Not ready yet
        figs = generate_reads_figures()
    elif measurement == 'Metabolites':
        figs = generate_metabolite_figures(studyId, measurement, experimentId, args)
    else:
        figs = generate_growth_figures(studyId, measurement, experimentId, args)

    fig_htmls = [
        fig.to_html(
            full_html=False,
            include_plotlyjs=False,
            default_width=f"{width}px",
        )
        for fig in figs
    ]

    return render_template('pages/dashboard/_figs.html', fig_htmls=fig_htmls)


def generate_growth_figures(studyId, measurement, experimentId, args):
    df_growth, _ = get_chart_data(studyId)
    df_growth, _ = filter_bioreplicates(df_growth, measurement, experimentId, args)

    fig = px.line(
        df_growth,
        x='Time',
        y=measurement,
        color='Biological_Replicate_id',
        title=f'{measurement} Plot for Experiment: {experimentId} per Biological replicate',
        labels={'Time': 'Hours'},
        markers=True
    )

    return [fig]

def generate_metabolite_figures(studyId, measurement, experimentId, args):
    df_growth, _ = get_chart_data(studyId)
    df_growth, bioreplicate_ids = filter_bioreplicates(df_growth, measurement, experimentId, args)

    non_metabolite_keys = set([
        'Position', 'Biological_Replicate_id', 'Time',
        'OD', 'Plate Counts', 'pH', 'FC',
    ])
    metabolite_keys = set(df_growth.keys()).difference(non_metabolite_keys)

    figures = []
    for bioreplicate_id in bioreplicate_ids:
        filtered_df = df_growth[df_growth['Biological_Replicate_id'] == bioreplicate_id]
        melted_df = filtered_df.melt(
            id_vars=['Time', 'Biological_Replicate_id'],
            value_vars=metabolite_keys,
            var_name='Metabolites',
            value_name='mM'
        )

        figures.append(px.line(
            melted_df,
            x='Time',
            y='mM',
            color='Metabolites',
            title=f'Metabolite Concentrations: {bioreplicate_id} per Metabolite',
            labels={'Time': 'Hours'},
            markers=True
        ))

    return figures

def generate_reads_figures(studyId, experimentId, args):
    return []


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


def first_bioreplicate(data, args):
    bioreplicate_id = None
    include_average = False
    label = None

    for arg in args:
        if arg.endswith(':_average'):
            include_average = True
            break
        elif arg.startswith('bioreplicate:'):
            bioreplicate_id = arg[len('bioreplicate:'):]
            break

    if include_average:
        data = data.groupby('Time')[measurement].mean().reset_index()
        label = f"Average {experimentId}"
        data['Biological_Replicate_id'] = label
    elif bioreplicate_id is not None:
        data = data[data['Biological_Replicate_id'] == bioreplicate_id]
        label = bioreplicate_id

    return (data, label)


def filter_bioreplicates(data, measurement, experimentId, args):
    bioreplicate_ids = []
    include_average = False

    for arg in args:
        if arg.endswith(':_average'):
            include_average = True
        elif arg.startswith('bioreplicate:'):
            bioreplicate_ids.append(arg[len('bioreplicate:'):])

    data = data[data['Biological_Replicate_id'].isin(bioreplicate_ids)]

    if include_average:
        mean_df_specific_ids = data.groupby('Time')[measurement].mean().reset_index()
        mean_df_specific_ids['Biological_Replicate_id'] = f"Average {experimentId}"
        data = pd.concat([data, mean_df_specific_ids], ignore_index=True)

    return data, bioreplicate_ids

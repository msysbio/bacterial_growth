import os
import pandas as pd

# TODO: Needs to read data from the database and be moved somewhere
# appropriate with a `conn` argument. Or it might be removed.
def get_chart_data(studyId):
    filepath = os.path.realpath(__file__)
    current_dir = os.path.dirname(filepath)
    root_dir = os.path.dirname(current_dir)
    relative_path_to_src = os.path.join(root_dir, '../src')

    path = relative_path_to_src + f"/Data/Growth/{studyId}"
    growth_file = path + "/Growth_Metabolites.csv"
    reads_file = path + "/Sequencing_Reads.csv"

    df_growth = pd.read_csv(growth_file)
    subset_columns = df_growth.columns.drop('Position')
    # Drop rows where all values are NaN
    df_growth = df_growth.dropna(subset=subset_columns, how='all')

    df_reads = pd.read_csv(reads_file)

    return (df_growth, df_reads)

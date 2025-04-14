import io

import pandas as pd

from legacy.constants import GrowthTechniques

def get_techniques_metabolites(list_growth, list_metabolites, list_microbial_strains, raw_data_template):

    """
    Function that checks concordance between the growth measurement techniques and the uploaded data template:

    inputs:
        - list_growth: List of growth measurements selected from the interface in step 3
        - list_metabolites: List of metabolites selected from the interface in step 3

    Returns:
        - error_messages: a list of all the errors detected
    """
    error_messages = []
    growth_techniques = GrowthTechniques()
    try:
        # read the headers and check that the headers match the options choosen by the user in the interface

        # reads the data template sheet 1: Growth_Data_and_Metabolites
        df_excel_growth = pd.read_excel(raw_data_template, sheet_name='Growth_Data_and_Metabolites')

        if growth_techniques.rna in list_growth or growth_techniques.fc_ps or growth_techniques.plates_ps in list_growth:

            df_excel_abundances = pd.read_excel(raw_data_template, sheet_name='growth_per_species')
            columns_abundances = df_excel_abundances.columns

            # check that all the mandatory columns are in the excel
            assert 'Time' in columns_abundances, "ERROR, 'Time' missing in growth_per_species"
            assert'Biological_Replicate_id' in columns_abundances, "ERROR, 'Biological_Replicate_id' missing in growth_per_species"
            assert'Position' in columns_abundances, "ERROR, 'Position' missing in growth_per_species"
            empty_columns_abundances = df_excel_abundances.columns[df_excel_abundances.isnull().all()].tolist()
            filtered_empty_columns = [string for string in empty_columns_abundances if not string.endswith('_std')]
            # check that there is not empty columns in the sequencing reads sheet
            assert len(filtered_empty_columns) ==  0, "ERROR: missing mandatoy columns in growth_per_species"

            #check all columns fro the microbial strains are in the excel
            if growth_techniques.rna in list_growth:
                for i in list_microbial_strains:
                    microbial_read = f'{i}_reads'
                    microbial_reads_std = f'{i}_reads_std'
                    assert microbial_read in columns_abundances, f'ERROR: column {microbial_read} information is missing in template_raw_data'
                    assert microbial_reads_std in columns_abundances, f'ERROR: column {microbial_reads_std} is missing in template_raw_data'
            if growth_techniques.fc_ps in list_growth:
                for i in list_microbial_strains:
                    microbial_count = f'{i}_counts'
                    microbial_count_std = f'{i}_counts_std'
                    assert microbial_count in columns_abundances, f'ERROR: column {microbial_count} information is missing in template_raw_data'
                    assert microbial_count_std in columns_abundances, f'ERROR: column {microbial_count_std} is missing in template_raw_data'

        columns_growth = df_excel_growth.columns

        # check that all the mandatory headers are in the growth data sheet
        if growth_techniques.od in list_growth:
            assert 'OD' in columns_growth and 'OD_std' in columns_growth, "ERROR: 'OD' or 'OD_std' not found in template_raw_data"

        if growth_techniques.plates in list_growth:
            assert 'Plate_counts' in columns_growth and 'Plate_counts_std' in columns_growth, "ERROR: 'Plate_counts' or 'Plate_counts_std' not found in template_raw_data"
        if'Flow Cytometry (FC)'in list_growth:
            assert 'FC' in columns_growth and 'FC_std' in columns_growth, "ERROR: 'FC' or 'FC_std' not found in template_raw_data"

        for i in list_metabolites:
            metabolite_std = f'{i}_std'
            assert i in columns_growth, f'ERROR: metabolite {i} is missing in template_raw_data'
            assert metabolite_std in columns_growth, f'ERROR: column {metabolite_std} is missing in template_raw_data'

        # Create a list of columns that are empty to check that all the mandatory columns are not empty
        empty_columns_growth = df_excel_growth.columns[df_excel_growth.isnull().all()].tolist()
        for i in empty_columns_growth:
            assert i.endswith('_std') or i == 'pH', f'ERROR: Column {i} is not expected to be missing'

    # gets all the assertion errors
    except AssertionError as e:
        error_messages.append(str(e))  # Append the error message to the list

    return error_messages


def get_measures_growth(raw_data_template):
    """
    Function that creates a dictionary with replicate_id and the column name:

    inputs:
        - raw_data_template: raw data template uploaded by the user in the interface in step 4

    Returns:
        - filtered_measures_per_replicate: a dictionary of all the biological replicate ids and the growth measurements that were completed
        - filtered_metabolites_per_replicate: a dictionary of all the biological replicate ids and the metabolites that were completed
    """
    # read the raw data template sheet 1
    df_excel_growth = pd.read_excel(raw_data_template, sheet_name='Growth_Data_and_Metabolites')

    measures_per_replicate = {}

    # Iterate over groups based on Replicate_id
    for replicate_id, group_df in df_excel_growth.groupby('Biological_Replicate_id'):
        # Drop the Replicate_id column and check for non-empty values in each column
        non_empty_columns = group_df.drop(['Biological_Replicate_id', 'Time', 'Position'], axis=1).columns[group_df.drop(['Biological_Replicate_id', 'Time', 'Position'], axis=1).notnull().any()]
        # Convert the result to a list and store it in the dictionary
        measures_per_replicate[replicate_id] = non_empty_columns.tolist()

    measures = ['OD', 'OD_std','Plate_counts','Plate_counts_std','pH', 'FC', 'FC_std']
    # filters the ones that are not null per Biological_replicate_id
    filtered_measures_per_replicate = {key: [item for item in value if item in measures] for key, value in measures_per_replicate.items()}
    filtered_metabolites_per_replicate = {key: [item for item in value if item not in measures and not item.endswith('_std')] for key, value in measures_per_replicate.items()}

    return filtered_measures_per_replicate, filtered_metabolites_per_replicate

def get_measures_counts(raw_data_template):
    """
    Function that creates a dictionary with the replicate id and the microbial strain name completed:

    inputs:
        - raw_data_template: raw data template uploaded by the user in the interface in step 4

    Returns:
        - abundances_per_replicate: a dictionary with each replicate id completed in growth_per_species and the microbial strains measured
    """
    df_excel_abundances = pd.read_excel(raw_data_template, sheet_name='growth_per_species')

    abundances_per_replicate = {}

    # Iterate over groups based on Replicate_id
    for replicate_id, group_df in df_excel_abundances.groupby('Biological_Replicate_id'):
        # Drop the Replicate_id column and check for non-empty values in each column
        non_empty_columns = group_df.drop(['Biological_Replicate_id', 'Time', 'Position'], axis=1).columns[group_df.drop(['Biological_Replicate_id', 'Time', 'Position'], axis=1).notnull().any()]
        # Convert the result to a list and store it in the dictionary
        filtered_abundance_columns = [string.replace('_counts', '') for string in non_empty_columns if string.endswith('_counts')]
        abundances_per_replicate[replicate_id] = filtered_abundance_columns
    return abundances_per_replicate

def get_measures_reads(raw_data_template):
    """
    Function that creates a dictionary with the replicate id and the microbial strain name completed:

    inputs:
        - raw_data_template: raw data template uploaded by the user in the interface in step 4

    Returns:
        - reads_per_replicate: a dictionary with each replicate id completed in growth_per_species and the microbial strains measured
    """
    df_excel_reads = pd.read_excel(raw_data_template, sheet_name='growth_per_species')

    reads_per_replicate = {}

    # Iterate over groups based on Replicate_id
    for replicate_id, group_df in df_excel_reads.groupby('Biological_Replicate_id'):
        # Drop the Replicate_id column and check for non-empty values in each column
        non_empty_columns = group_df.drop(['Biological_Replicate_id', 'Time', 'Position'], axis=1).columns[group_df.drop(['Biological_Replicate_id', 'Time', 'Position'], axis=1).notnull().any()]
        # Convert the result to a list and store it in the dictionary
        filtered_reads_columns = [string.replace('_reads', '') for string in non_empty_columns if string.endswith('_reads')]
        reads_per_replicate[replicate_id] = filtered_reads_columns
    return reads_per_replicate

def get_replicate_metadata(raw_data_template):
    """
    Function that creates a dictionary with the replicate metadata

    inputs:
        - raw_data_template: raw data template uploaded by the user in the interface in step 4

    Returns:
        - reads_per_replicate: a dictionary with the information completed in the Replicate_metadata sheet
    """
    df_replicate_metadata = pd.read_excel(io.BytesIO(raw_data_template), sheet_name='Replicate metadata')
    rep_metadata_dicts = {}
    rep_metadata_dicts = {col: df_replicate_metadata[col].tolist() for col in df_replicate_metadata.columns}
    return rep_metadata_dicts


def save_data_to_csv(output_csv_path_growth,output_csv_path_reads,raw_data_template):
    """
    Function that two files given the raw data template, one stores all the growth + metabolites data and
    the other stores the sequencing and count data from 16S RNA Seq OR FC

    input:
        - output_csv_path_growth: file path to store the growth data file
        - output_csv_path_reads: file path to store the sequencing data file
        - raw_data_template: raw data template file

    Returns:
        - two csv files stored in the path : tmp_data/<StudyId>/.., the data does not contain empty columns or empty rows.
    """
    df_excel_growth = pd.read_excel(raw_data_template, sheet_name='Growth_Data_and_Metabolites')
    # Drop columns with NaN values
    df_excel_growth = df_excel_growth.dropna(axis=1, how='all')
    # Drop rows where all values are NaN
    df_excel_growth = df_excel_growth.dropna(axis=0, how='all')
    if not df_excel_growth.empty:
        df_excel_growth.to_csv(output_csv_path_growth, index=False)

    df_excel_reads = pd.read_excel(raw_data_template, sheet_name='growth_per_species')
    # Drop columns with NaN values
    df_excel_reads = df_excel_reads.dropna(axis=1, how='all')
    subset_columns = df_excel_reads.columns.drop('Position')
    # Drop rows where all values are NaN
    df_excel_reads = df_excel_reads.dropna(subset=subset_columns, how='all')
    if not df_excel_reads.empty:
        df_excel_reads.to_csv(output_csv_path_reads, index=False)

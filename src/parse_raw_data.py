import pandas as pd


def get_techniques_metabolites(list_growth, list_metabolites, raw_data_template):

    error_messages = []
    try:
        #read the headers and check that the headers match the lists choosen by the user
        df_excel_growth = pd.read_excel(raw_data_template, sheet_name='Growth_Data_and_Metabolites')
        if '16S rRNA-seq' in list_growth:
            df_excel_abundances = pd.read_excel(raw_data_template, sheet_name='Sequencing_Read_Adundances')
            columns_abundances = df_excel_abundances.columns
            assert 'Time' in columns_abundances, "ERROR, 'Time' missing in Sequencing_Read_Adundances"
            assert'Replicate_id' in columns_abundances, "ERROR, 'Replicate_id' missing in Sequencing_Read_Adundances"
            empty_columns_abundances = df_excel_abundances.columns[df_excel_abundances.isnull().all()].tolist()
            assert len(empty_columns_abundances) ==  0, "ERROR: missing columns in Sequencing_Read_Adundances"

        columns_growth = df_excel_growth.columns

        if 'Optical Density (OD)' in list_growth:
            assert 'OD' in columns_growth and 'OD_std' in columns_growth, "ERROR: 'OD' or 'OD_std' not found in template_raw_data"
        if'Plate-Counts'in list_growth:
            assert 'Plate_counts' in columns_growth and 'Plate_counts_std' in columns_growth, "ERROR: 'Plate_counts' or 'Plate_counts_std' not found in template_raw_data"
        if 'Flow Cytometry (FC)' in list_growth:
            assert 'FC' in columns_growth and 'FC_std' in columns_growth, "ERROR: 'FC' or 'FC_std' not found in template_raw_data"

        for i in list_metabolites:
            assert i in columns_growth, f'ERROR: metabolite {i} is missing in template_raw_data'
        
        # Create a list of columns that are empty
        empty_columns_growth = df_excel_growth.columns[df_excel_growth.isnull().all()].tolist()
        for i in empty_columns_growth:
            assert i in ['pH','OD_std', 'Plate_counts_std', 'FC_std'], f'ERROR: Column {i} is not expected to be missing'
    
    except AssertionError as e:
        error_messages.append(str(e))  # Append the error message to the list

    return error_messages

    
def get_measures_growth(raw_data_template):
    df_excel_growth = pd.read_excel(raw_data_template, sheet_name='Growth_Data_and_Metabolites')

    measures_per_replicate = {}
    
    # Iterate over groups based on Replicate_id
    for replicate_id, group_df in df_excel_growth.groupby('Replicate_id'):
        # Drop the Replicate_id column and check for non-empty values in each column
        non_empty_columns = group_df.drop(['Replicate_id', 'Time'], axis=1).columns[group_df.drop(['Replicate_id', 'Time'], axis=1).notnull().any()]
        # Convert the result to a list and store it in the dictionary
        measures_per_replicate[replicate_id] = non_empty_columns.tolist()

    measures = ['OD', 'OD_std','Plate_counts','Plate_counts_std','FC','FC_std','pH']
    filtered_measures_per_replicate = {key: [item for item in value if item in measures] for key, value in measures_per_replicate.items()}
    filtered_metabolites_per_replicate = {key: [item for item in value if item not in measures] for key, value in measures_per_replicate.items()}
    return filtered_measures_per_replicate, filtered_metabolites_per_replicate

def get_measures_abundances(raw_data_template):
    df_excel_abundances = pd.read_excel(raw_data_template, sheet_name='Sequencing_Read_Adundances')

    abundances_per_replicate = {}
    
    # Iterate over groups based on Replicate_id
    for replicate_id, group_df in df_excel_abundances.groupby('Replicate_id'):
        # Drop the Replicate_id column and check for non-empty values in each column
        non_empty_columns = group_df.drop(['Replicate_id', 'Time'], axis=1).columns[group_df.drop(['Replicate_id', 'Time'], axis=1).notnull().any()]
        # Convert the result to a list and store it in the dictionary
        abundances_per_replicate[replicate_id] = non_empty_columns.tolist()
    return abundances_per_replicate


import os
import yaml

import pandas as pd


# functon that loads a yaml file  into a df
def load_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


def test_study_yaml(data):
    """
    Function that test the study yaml dataframe, checking that all the mandatory columns are not .nan or in the right format
    inputs:
        - data: dataframe corresponding to the excel sheet

    Returns:
        - errors: List of errors if found.
    """
    df = pd.DataFrame(data)
    errors = []
    for column in df.columns:
        if column == 'Study_UniqueID':
            if not (pd.api.types.is_float_dtype(df[column]) or pd.api.types.is_string_dtype(df[column])):
                errors.append(f"Study: Column '{column}' must be of type string or blank.")
        else:
            if not (pd.api.types.is_string_dtype(df[column])):
                errors.append(f"Study: Column '{column}' must be of type string. No blank cells allowed.")
    return errors


def test_experiments_yaml(data):
    """
    Function that test the experiments yaml dataframe, checking that all the mandatory columns are not .nan or in the right format
    inputs:
        - data: dataframe corresponding to the excel sheet

    Returns:
        - errors: List of errors if found.
    """
    df = pd.DataFrame(data)
    errors = []
    for column in df.columns:
        if column == 'Biological_Replicates_Number':
            if not (pd.api.types.is_numeric_dtype(df[column])):
                errors.append(f"Experiments: Column '{column}' must be of  must a numeric value. No blank cells allowed.")
        elif column == 'Control_Description':
            if not (pd.api.types.is_float_dtype(df[column]) or pd.api.types.is_string_dtype(df[column])):
                errors.append(f"Experiments: Column '{column}' must be of type string or blank.")
        else:
            if not (pd.api.types.is_string_dtype(df[column])):
                errors.append(f"Experiments: Column '{column}' must be of type string. No blank cells allowed.")

    return errors


def test_compartments_yaml(data):
    """
    Function that test the compartments yaml dataframe, checking that all the mandatory columns are not .nan or in the right format
    inputs:
        - data: dataframe corresponding to the excel sheet

    Returns:
        - errors: List of errors if found.
    """
    df = pd.DataFrame(data)
    errors = []
    for column in df.columns:
        if column == 'Compartment_ID' or column == 'Medium_Name':
            if not (pd.api.types.is_string_dtype(df[column])):
                errors.append(f"Compartments: Column '{column}' must be of type string. No blank cells allowed.")
        elif column == 'Compartment_StirringMode' or column == 'Medium_Link':
            if not (pd.api.types.is_string_dtype(df[column]) or pd.api.types.is_float_dtype(df[column])):
                errors.append(f"Compartments: Column '{column}' must be of type string or blank.")
        elif column == 'Compartment_Volume' or column == 'O2%' or column == 'Inoculum_Concentration' or column == 'Inoculum_Volume':
            if not (pd.api.types.is_numeric_dtype(df[column])):
                errors.append(f"Compartments: Column '{column}' must be of  must a numeric value. No blank cells allowed.")
        elif column == 'Carbon_Source':
            if not (df[column].isin([0, 1]).all() or pd.api.types.is_float_dtype(df[column])):
                errors.append(f"Compartments: Values in column '{column}' must be 0, 1, or blank.")
        else:
            if not (pd.api.types.is_numeric_dtype(df[column]) or pd.api.types.is_float_dtype(df[column])):
                errors.append(f"Compartments: Column '{column}' must be of  must a numeric or blank value.")
    return errors


def test_comu_members_yaml(data):
    """
    Function that test the community members yaml dataframe, checking that all the mandatory columns are not .nan or in the right format
    inputs:
        - data: dataframe corresponding to the excel sheet

    Returns:
        - errors: List of errors if found.
    """
    df = pd.DataFrame(data)
    errors = []
    for column in df.columns:
        if column == 'Defined':
            if not df[column].isin([0, 1]).all():
                errors.append(f"Community members: Column '{column}' must be of  must 0 or 1. No blank cells allowed.")
        elif column == 'NCBI_ID':
            if not (pd.api.types.is_numeric_dtype(df[column])):
                errors.append(f"Community members: Column '{column}' must be of  must a numeric value. No blank cells allowed.")
        elif column == 'Description':
            # look what is the data type of description when is blank or string
            # if not (pd.api.types.is_string_dtype(df[column]) or pd.api.types.is_float_dtype(df[column])):
            #    errors.append(f"Community: Column '{column}' must be of type string or blank.")
            pass
        else:
            if not (pd.api.types.is_string_dtype(df[column])):
                errors.append(f"Community members: Column '{column}' must be of type string. No blank cells allowed.")
    return errors


def test_communities_yaml(data):
    """
    Function that test the communitites yaml dataframe, checking that all the mandatory columns are not .nan or in the right format
    inputs:
        - data: dataframe corresponding to the excel sheet

    Returns:
        - errors: List of errors if found.
    """
    df = pd.DataFrame(data)
    errors = []
    for column in df.columns:
        if not pd.api.types.is_string_dtype(df[column]):
            errors.append(f"Communities: Column '{column}' must be of type string. No blank cells allowed.")

    return errors


def test_perturbation_yaml(data):
    """
    Function that test the perturbations yaml dataframe, checking that all the mandatory columns are not .nan or in the right format
    inputs:
        - data: dataframe corresponding to the excel sheet

    Returns:
        - errors: List of errors if found.
    """
    df = pd.DataFrame(data)
    errors = []
    if pd.api.types.is_string_dtype(df['Perturbation_ID']):
        for column in df.columns:
            if column == 'Experiment_ID' or column == 'Perturbation_Description' or column == 'Perturbation_EndTime' or column == 'Perturbation_StartTime':
                if not (pd.api.types.is_string_dtype(df[column])):
                    errors.append(f"Perturbations: Column '{column}' must be of type string. No blank cells allowed.")
            elif column == 'Perturbation_MaximumValue' or column == 'Perturbation_MinimumValue':
                if not (pd.api.types.is_numeric_dtype(df[column]) or pd.api.types.is_float_dtype(df[column])):
                    errors.append(f"Perturbations: Column '{column}' must be of  must a numeric or blank value.")
            else:
                if not (pd.api.types.is_string_dtype(df[column]) or pd.api.types.is_float_dtype(df[column])):
                    errors.append(f"Perturbations: Column '{column}' must be of type string or blank.")

    if pd.api.types.is_string_dtype(df['OLD_Community_ID']):
        if not (pd.api.types.is_string_dtype(df['NEW_Community_ID'])):
            errors.append("Perturbations: Column 'NEW_Community_ID' must be of type string. No blank cells allowed.")
    if pd.api.types.is_string_dtype(df['OLD_Compartment_ID']):
        if not (pd.api.types.is_string_dtype(df['NEW_Compartment_ID'])):
            errors.append("Perturbations: Column 'NEW_Compartment_ID' must be of type string. No blank cells allowed.")
    if (pd.api.types.is_numeric_dtype(df['Perturbation_MaximumValue']) and pd.api.types.is_numeric_dtype(df['Perturbation_MinimumValue'])):
        logic_check = df['Perturbation_MaximumValue'] > df['Perturbation_MinimumValue']
        if not logic_check.all():
            errors.append("Perturbations: Column 'Perturbation_MaximumValue' must be bigger than 'Perturbation_MinimumValue'.")
    if (pd.api.types.is_string_dtype(df['Perturbation_EndTime']) and pd.api.types.is_string_dtype(df['Perturbation_StartTime'])):
        df['Perturbation_EndTime'] = pd.to_datetime(df['Perturbation_EndTime']).dt.time
        df['Perturbation_StartTime'] = pd.to_datetime(df['Perturbation_StartTime']).dt.time
        logic_check = df['Perturbation_EndTime'] > df['Perturbation_StartTime']
        if not logic_check.all():
            errors.append("Perturbations: 'Perturbation_EndTime' must be bigger than 'Perturbation_StartTime'.")

    return errors

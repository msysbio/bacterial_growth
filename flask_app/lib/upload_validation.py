import os
import yaml

import pandas as pd

from flask_app.lib.check_yaml import test_study_yaml, test_experiments_yaml, test_compartments_yaml, test_comu_members_yaml, test_communities_yaml, test_perturbation_yaml

# TODO Temporary:
root_folder = os.path.abspath(os.path.dirname(__file__) + '/../../')

LOCAL_DIRECTORY           = os.path.join(root_folder, "")
LOCAL_DIRECTORY_APP       = os.path.join(LOCAL_DIRECTORY, "app")
LOCAL_DIRECTORY_TEMPLATES = os.path.join(LOCAL_DIRECTORY_APP, "templates")
LOCAL_DIRECTORY_YAML      = os.path.join(LOCAL_DIRECTORY_TEMPLATES, "yaml_templates")


def validate_upload(study_template, data_template):
    errors = []

    if len(study_template) == 0:
        errors.append('Missing study template')
    if len(data_template) == 0:
        errors.append("Missing data template")

    if len(errors) > 0:
        return errors

    os.makedirs(LOCAL_DIRECTORY_TEMPLATES, exist_ok=True)
    os.makedirs(LOCAL_DIRECTORY_YAML, exist_ok=True)

    # Get all the yaml files
    parse_ex_to_yaml(LOCAL_DIRECTORY_YAML, study_template)

    # Define the yaml files path
    info_file_study = os.path.join(LOCAL_DIRECTORY_YAML, 'STUDY.yaml')
    info_file_experiments = os.path.join(LOCAL_DIRECTORY_YAML, 'EXPERIMENTS.yaml')
    info_compart_file = os.path.join(LOCAL_DIRECTORY_YAML, 'COMPARTMENTS.yaml')
    info_mem_file = os.path.join(LOCAL_DIRECTORY_YAML, 'COMMUNITY_MEMBERS.yaml')
    info_comu_file = os.path.join(LOCAL_DIRECTORY_YAML, 'COMMUNITIES.yaml')
    info_pert_file = os.path.join(LOCAL_DIRECTORY_YAML, 'PERTURBATIONS.yaml')

    # Do the test to the yaml files according to the sheet
    data_study_yaml = load_yaml(info_file_study)
    errors = test_study_yaml(data_study_yaml)

    data_experiment_yaml = load_yaml(info_file_experiments)
    errors.extend(test_experiments_yaml(data_experiment_yaml))

    data_compartment_yaml = load_yaml(info_compart_file)
    errors.extend(test_compartments_yaml(data_compartment_yaml))

    data_comu_members_yaml = load_yaml(info_mem_file)
    errors.extend(test_comu_members_yaml(data_comu_members_yaml))

    data_comu = load_yaml(info_comu_file)
    errors.extend(test_communities_yaml(data_comu))

    data_pertu = load_yaml(info_pert_file)
    errors.extend(test_perturbation_yaml(data_pertu))

    return errors


def parse_ex_to_yaml(LOCAL_DIRECTORY_YAML, template_excel):
    """
    Function that parse the metadata template that the user uploads in step 4 and creates a yaml file
    per sheet in the excel

    inputs:
        - LOCAL_DIRECTORY: path were the yaml files are going to be saved
        - template_excel: matadata excel file uploaded by the user

    Returns:
        - yaml file per sheet in metadata excel: STUDY.yaml, EXPERIMENTS.yaml, COMPARTMENTS.yaml,
        COMMUNITY_MEMBERS.yaml, COMMUNITIES.yaml, PERTURBATIONS.yaml
    """

    # Read the completed Excel file
    df_excel_1 = pd.read_excel(template_excel, engine='openpyxl',sheet_name='STUDY')
    df_excel_2 = pd.read_excel(template_excel, engine='openpyxl' ,sheet_name='EXPERIMENTS')
    df_excel_3 = pd.read_excel(template_excel, engine='openpyxl',sheet_name='COMPARTMENTS')
    df_excel_4 = pd.read_excel(template_excel, engine='openpyxl',sheet_name='COMMUNITY_MEMBERS')
    df_excel_5 = pd.read_excel(template_excel, engine='openpyxl',sheet_name='COMMUNITIES')
    df_excel_6 = pd.read_excel(template_excel, engine='openpyxl',sheet_name='PERTURBATIONS')

    # Convert start_time and end_time to strings
    df_excel_6['Perturbation_StartTime'] = df_excel_6['Perturbation_StartTime'].astype(str)
    df_excel_6['Perturbation_EndTime'] = df_excel_6['Perturbation_EndTime'].astype(str)


    # Initialize dictionaries for each prefix
    data_dicts = {}

    data_dicts = {col: df_excel_1[col].tolist() for col in df_excel_1.columns}


    data_dicts2 = {}
    data_dicts2 = {col: df_excel_2[col].tolist() for col in df_excel_2.columns}

    data_dicts3 = {}
    data_dicts3 = {col: df_excel_3[col].tolist() for col in df_excel_3.columns}


    data_dicts4 = {}
    data_dicts4 = {col: df_excel_4[col].tolist() for col in df_excel_4.columns}

    data_dicts5 = {}
    data_dicts5 = {col: df_excel_5[col].tolist() for col in df_excel_5.columns}

    data_dicts6 = {}
    data_dicts6 = {col: df_excel_6[col].tolist() for col in df_excel_6.columns}
    # Convert DataFrame to YAML
    yaml_data = yaml.dump(data_dicts)
    yaml_data2 = yaml.dump(data_dicts2)
    yaml_data3 = yaml.dump(data_dicts3)
    yaml_data4 = yaml.dump(data_dicts4)
    yaml_data5 = yaml.dump(data_dicts5)
    yaml_data6 = yaml.dump(data_dicts6)


    template_filename_yaml_STUDY = os.path.join(LOCAL_DIRECTORY_YAML, 'STUDY.yaml')
    template_filename_yaml_EXPERIMENTS = os.path.join(LOCAL_DIRECTORY_YAML, 'EXPERIMENTS.yaml')
    template_filename_yaml_COMPARTMENTS = os.path.join(LOCAL_DIRECTORY_YAML, 'COMPARTMENTS.yaml')
    template_filename_yaml_COMMUNITY_MEMBERS = os.path.join(LOCAL_DIRECTORY_YAML, 'COMMUNITY_MEMBERS.yaml')
    template_filename_yaml_COMMUNITIES = os.path.join(LOCAL_DIRECTORY_YAML, 'COMMUNITIES.yaml')
    template_filename_yaml_PERTURBATIONS = os.path.join(LOCAL_DIRECTORY_YAML, 'PERTURBATIONS.yaml')

    all_yamls = [template_filename_yaml_STUDY, template_filename_yaml_EXPERIMENTS, template_filename_yaml_COMPARTMENTS,
                 template_filename_yaml_COMMUNITY_MEMBERS, template_filename_yaml_COMMUNITIES, template_filename_yaml_PERTURBATIONS]
    for yamlfile in all_yamls:
        if os.path.isfile(yamlfile):
            os.remove(yamlfile)
    print("\n\n\n\n\n  tmp yamls")
    print(os.listdir(LOCAL_DIRECTORY_YAML))


    # Write YAML data to a file
    with open(template_filename_yaml_STUDY, "w") as yaml_file:
        yaml_file.write(yaml_data)

    # Write YAML data to a file
    with open(template_filename_yaml_EXPERIMENTS, "w") as yaml_file:
        yaml_file.write(yaml_data2)

    # Write YAML data to a file
    with open(template_filename_yaml_COMPARTMENTS, "w") as yaml_file:
        yaml_file.write(yaml_data3)

    with open(template_filename_yaml_COMMUNITY_MEMBERS, "w") as yaml_file:
        yaml_file.write(yaml_data4)

    with open(template_filename_yaml_COMMUNITIES, "w") as yaml_file:
        yaml_file.write(yaml_data5)

    with open(template_filename_yaml_PERTURBATIONS, "w") as yaml_file:
        yaml_file.write(yaml_data6)


def load_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


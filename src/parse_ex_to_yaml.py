import pandas as pd
import yaml
from constants import LOCAL_DIRECTORY

template_filename = LOCAL_DIRECTORY + '/metadata_template2.xlsx'
# Read the completed Excel file
df_excel_1 = pd.read_excel(template_filename, sheet_name='STUDY')
df_excel_2 = pd.read_excel(template_filename, sheet_name='EXPERIMENTS')
df_excel_3 = pd.read_excel(template_filename, sheet_name='COMPARTMENTS')
df_excel_4 = pd.read_excel(template_filename, sheet_name='COMMUNITY_MEMBERS')
df_excel_5 = pd.read_excel(template_filename, sheet_name='COMMUNITIES')
df_excel_6 = pd.read_excel(template_filename, sheet_name='PERTURBATIONS')

# Convert start_time and end_time to strings
df_excel_6['Perturbation_StartTime'] = df_excel_6['Perturbation_StartTime'].astype(str)
df_excel_6['Perturbation_EndTime'] = df_excel_6['Perturbation_EndTime'].astype(str)


NUM_ROWS1, num_columns1 = df_excel_1.shape
NUM_ROWS2, num_columns2 = df_excel_2.shape
NUM_ROWS3, num_columns3 = df_excel_3.shape
NUM_ROWS4, num_columns4 = df_excel_4.shape
NUM_ROWS5, num_columns5= df_excel_5.shape
NUM_ROWS6, num_columns6= df_excel_6.shape

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

template_filename_yaml_STUDY = LOCAL_DIRECTORY + 'STUDY.yaml'
template_filename_yaml_EXPERIMENTS = LOCAL_DIRECTORY + 'EXPERIMENTS.yaml'
template_filename_yaml_COMPARTMENTS = LOCAL_DIRECTORY + 'COMPARTMENTS.yaml'
template_filename_yaml_COMMUNITY_MEMBERS = LOCAL_DIRECTORY + 'COMMUNITY_MEMBERS.yaml'
template_filename_yaml_COMMUNITIES = LOCAL_DIRECTORY + 'COMMUNITIES.yaml'
template_filename_yaml_PERTURBATIONS = LOCAL_DIRECTORY + 'PERTURBATIONS.yaml'
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




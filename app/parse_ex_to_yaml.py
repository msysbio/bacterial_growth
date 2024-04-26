import pandas as pd
import yaml
from constants import LOCAL_DIRECTORY

template_filename = LOCAL_DIRECTORY + 'template_new changes_cases_data.xlsx'
# Read the completed Excel file
df_excel_1 = pd.read_excel(template_filename, sheet_name='STUDY_DATA')
df_excel_2 = pd.read_excel(template_filename, sheet_name='COMPARTMENTS')
df_excel_3 = pd.read_excel(template_filename, sheet_name='COMUNITY_MEMBERS')
df_excel_4 = pd.read_excel(template_filename, sheet_name='COMUNITIES')
df_excel_5 = pd.read_excel(template_filename, sheet_name='PERTURBATIONS')


NUM_ROWS1, num_columns1 = df_excel_1.shape
NUM_ROWS2, num_columns2 = df_excel_2.shape
NUM_ROWS3, num_columns3 = df_excel_3.shape
NUM_ROWS4, num_columns4 = df_excel_4.shape
NUM_ROWS5, num_columns5= df_excel_5.shape

# Initialize dictionaries for each prefix
data_dicts = {}

grouped_prefixs = ['Event', 'Compartment', 'TechnicalReplicates', 'Cultivation' , 'Blank','Plate','Comunity','Growth']
# Iterate over the columns of the DataFrame

data_dicts = {}
data_dicts = {col: df_excel_1[col].tolist() for col in df_excel_1.columns}


data_dicts2 = {}

#for column in df_excel_2.columns:
    #prefix = column.split("_")[0]  # Get the prefix of the column
    #if prefix not in data_dicts2:
    #    data_dicts2[prefix] = {}
data_dicts2 = {col: df_excel_2[col].tolist() for col in df_excel_2.columns}
 #   data_dicts2[column] = df_excel_2[column].tolist()



data_dicts3 = {}
data_dicts3 = {col: df_excel_3[col].tolist() for col in df_excel_3.columns}


data_dicts4 = {}
data_dicts4 = {col: df_excel_4[col].tolist() for col in df_excel_4.columns}

data_dicts5 = {}
data_dicts5 = {col: df_excel_5[col].tolist() for col in df_excel_5.columns}
# Convert DataFrame to YAML
yaml_data = yaml.dump(data_dicts)
yaml_data2 = yaml.dump(data_dicts2)
yaml_data3 = yaml.dump(data_dicts3)
yaml_data4 = yaml.dump(data_dicts4)
yaml_data5 = yaml.dump(data_dicts5)

template_filename_yaml = LOCAL_DIRECTORY + 'submission_yaml.yaml'
template_filename_yaml_compart = LOCAL_DIRECTORY + 'submission_yaml_compart.yaml'
template_filename_yaml_bact = LOCAL_DIRECTORY + 'submission_yaml_mem.yaml'
template_filename_yaml_comu = LOCAL_DIRECTORY + 'submission_yaml_comu.yaml'
template_filename_yaml_pertu = LOCAL_DIRECTORY + 'submission_yaml_pertu.yaml'
# Write YAML data to a file
with open(template_filename_yaml, "w") as yaml_file:
    yaml_file.write(yaml_data)

# Write YAML data to a file
with open(template_filename_yaml_compart, "w") as yaml_file:
    yaml_file.write(yaml_data2)

# Write YAML data to a file
with open(template_filename_yaml_bact, "w") as yaml_file:
    yaml_file.write(yaml_data3)

with open(template_filename_yaml_bact, "w") as yaml_file:
    yaml_file.write(yaml_data3)

with open(template_filename_yaml_comu, "w") as yaml_file:
    yaml_file.write(yaml_data4)

with open(template_filename_yaml_pertu, "w") as yaml_file:
    yaml_file.write(yaml_data5)



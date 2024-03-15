import pandas as pd
import yaml
from constants import LOCAL_DIRECTORY

template_filename = LOCAL_DIRECTORY + 'submission_excel_template.xlsx'
# Read the completed Excel file
df_excel_1 = pd.read_excel(template_filename, sheet_name='STUDY_DATA')
df_excel_2 = pd.read_excel(template_filename, sheet_name='COMUNITY_MEMBERS')


NUM_ROWS1, num_columns1 = df_excel_1.shape
NUM_ROWS2, num_columns2 = df_excel_1.shape

# Initialize dictionaries for each prefix
data_dicts = {}

grouped_prefixs = ['Reactor','Media','Blank','Inoculum','Initial','Plate','Files','Antibiotic','Carbon','Comunity']
# Iterate over the columns of the DataFrame

for column in df_excel_1.columns:
    prefix = column.split("_")[0]  # Get the prefix of the column

    if prefix in grouped_prefixs:
        if column not in data_dicts['BiologicalReplicate']:
            data_dicts['BiologicalReplicate'][column] = {}
        data_dicts['BiologicalReplicate'][column] = df_excel_1[column].tolist()

    # If the prefix dictionary doesn't exist, create it
    if prefix not in grouped_prefixs:
        if prefix not in data_dicts:
            data_dicts[prefix] = {}
        data_dicts[prefix][column] = df_excel_1[column].tolist()

data_dicts2 = {}

for column in df_excel_2.columns:
    prefix = column.split("_")[0]  # Get the prefix of the column
    if prefix not in data_dicts2:
        data_dicts2[prefix] = {}
    data_dicts2[prefix][column] = df_excel_2[column].tolist()


# Convert DataFrame to YAML
yaml_data = yaml.dump(data_dicts)
yaml_data2 = yaml.dump(data_dicts2)

template_filename_yaml = LOCAL_DIRECTORY + 'submission_yaml.yaml'
template_filename_yaml2 = LOCAL_DIRECTORY + 'submission_yaml2.yaml'
# Write YAML data to a file
with open(template_filename_yaml, "w") as yaml_file:
    yaml_file.write(yaml_data)

# Write YAML data to a file
with open(template_filename_yaml2, "w") as yaml_file:
    yaml_file.write(yaml_data2)


#file="C:/Users/sofia/Desktop/local_thesis_files/yml_files/study_information.yml"
#with open(template_filename_yaml, "r") as yaml_file:
#    yaml_data_read = yaml.safe_load(yaml_file)

#print(yaml_data_read['BiologicalReplicate_Name'])

#print("YAML file created successfully!")
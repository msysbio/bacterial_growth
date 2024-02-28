import pandas as pd
import yaml
from constants import LOCAL_DIRECTORY

template_filename = LOCAL_DIRECTORY + 'submission_excel_template.xlsx'
# Read the completed Excel file
df = pd.read_excel(template_filename)

# Initialize dictionaries for each prefix
data_dicts = {}
headers = df.columns.tolist()

grouped_prefixs = ['Reactor','Media','Bacteria','Blank','Inoculum','Initial','Plate','Files','Antibiotic','Carbon']
# Iterate over the columns of the DataFrame

for column in df.columns:
    prefix = column.split("_")[0]  # Get the prefix of the column

    if prefix in grouped_prefixs:
        if prefix not in data_dicts['BiologicalReplicate']:
            data_dicts['BiologicalReplicate'][prefix] = {}
        data_dicts['BiologicalReplicate'][prefix][column] = df[column].tolist()

    # If the prefix dictionary doesn't exist, create it
    if prefix not in grouped_prefixs:
        if prefix not in data_dicts:
            data_dicts[prefix] = {}
        data_dicts[prefix][column] = df[column].tolist()



# Convert DataFrame to YAML
yaml_data = yaml.dump(data_dicts)

template_filename_yaml = LOCAL_DIRECTORY + 'submission_yaml.yaml'
# Write YAML data to a file
with open(template_filename_yaml, "w") as yaml_file:
    yaml_file.write(yaml_data)


#file="C:/Users/sofia/Desktop/local_thesis_files/yml_files/study_information.yml"
#with open(template_filename_yaml, "r") as yaml_file:
#    yaml_data_read = yaml.safe_load(yaml_file)

#print(yaml_data_read['BiologicalReplicate_Name'])

print("YAML file created successfully!")
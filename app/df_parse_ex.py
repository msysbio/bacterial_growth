import pandas as pd
import yaml
from constants import LOCAL_DIRECTORY

def parse_excel(df_excel_1,df_excel_2,df_excel_3,df_excel_4):
# Read the completed Excel file
    # Initialize dictionaries for each prefix
    data_dicts = {}

    grouped_prefixs = ['Replicate', 'Compartment', 'TechnicalReplicate', 'Cultivation' , 'Blank','Plate','Comunity','Growth']
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

    #for column in df_excel_2.columns:
        #prefix = column.split("_")[0]  # Get the prefix of the column
        #if prefix not in data_dicts2:
        #    data_dicts2[prefix] = {}
    data_dicts2 = {col: df_excel_2[col].tolist() for col in df_excel_2.columns}
    #   data_dicts2[column] = df_excel_2[column].tolist()



    data_dicts3 = {}

    for column in df_excel_3.columns:
        prefix = column.split("_")[0]  # Get the prefix of the column
        if prefix not in data_dicts3:
            data_dicts3[prefix] = {}
        data_dicts3[prefix][column] = df_excel_3[column].tolist()


    data_dicts4 = {}

    for column in df_excel_4.columns:
        prefix = column.split("_")[0]  # Get the prefix of the column

        # If the prefix dictionary doesn't exist, create it
        if prefix not in grouped_prefixs:
            if prefix not in data_dicts4:
                data_dicts4[prefix] = {}
            data_dicts4[prefix][column] = df_excel_4[column].tolist()


    # Convert DataFrame to YAML
    yaml_data = yaml.dump(data_dicts)
    yaml_data2 = yaml.dump(data_dicts2)
    yaml_data3 = yaml.dump(data_dicts3)
    yaml_data4 = yaml.dump(data_dicts4)

    template_filename_yaml = LOCAL_DIRECTORY + 'submission_yaml.yaml'
    template_filename_yaml_compart = LOCAL_DIRECTORY + 'submission_yaml_compart.yaml'
    template_filename_yaml_bact = LOCAL_DIRECTORY + 'submission_yaml_bact.yaml'
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


    with open(template_filename_yaml_pertu, "w") as yaml_file:
        yaml_file.write(yaml_data4)


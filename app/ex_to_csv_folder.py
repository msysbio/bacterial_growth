import os
import pandas as pd

def excel_to_csv_per_sheet(excel_file_path, studyId):
    # Create the output folder if it doesn't exist
    main_dir = 'bacterial_growth/src/Data'
    growth_dir = 'bacterial_growth/src/Data/Growth'
    metabolic_dir = 'bacterial_growth/src/Data/Metabolic'
    abundances_dir = 'bacterial_growth/src/Data/Abundance'
    if not os.path.exists(main_dir):
        os.makedirs(main_dir)

    if not os.path.exists(growth_dir):
        os.makedirs(growth_dir)

    if not os.path.exists(metabolic_dir):
        os.makedirs(metabolic_dir)

    if not os.path.exists(abundances_dir):
        os.makedirs(abundances_dir)

    # Read the Excel file
    xls = pd.ExcelFile(excel_file_path)

    # Iterate over each sheet in the Excel file
    for sheet_name in xls.sheet_names:
        # Read the current sheet into a DataFrame
        df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
        if sheet_name  == 'Growth_Data_and_Metabolites':
            csv_file_path = os.path.join(growth_dir, f"{studyId}_{sheet_name}.csv")
            df.to_csv(csv_file_path, index=False)
            print(f"Saved '{sheet_name}' as '{csv_file_path}'")
        if sheet_name == 'Sequencing_Read_Adundances':
            csv_file_path = os.path.join(abundances_dir, f"{studyId}_{sheet_name}.csv")
            df.to_csv(csv_file_path, index=False)
            print(f"Saved '{sheet_name}' as '{csv_file_path}'")

# Example usage:
excel_file_path = "example.xlsx"
output_folder = "output"
excel_to_csv_per_sheet(excel_file_path, output_folder)
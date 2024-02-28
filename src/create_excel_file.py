import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.comments import Comment
from openpyxl.utils import get_column_letter
from constants import LOCAL_DIRECTORY


# Create a new workbook
wb = Workbook()

# Select the active worksheet
ws = wb.active

# Add headers to the columns
headers = {
    'Study_ID': 'Complete with the ID provided before for your study. Do NOT add spaces.',
    'Study_Name' : 'Give an informative name to your study.',
    'Study_Description': 'Complete with a clear an concise description.',
    'Study_PublicationURL': 'Fill in with the publication URL if published.',
    'BiologicalReplicate_Name': 'Name of the biological replicate. Each row is a DIFFERENT biological replicate.',
    'BiologicalReplicate_Description': 'Description of the biological replicate.',
    'Reactor_Name': 'Name of the reactor.',
    'Reactor_Description': 'Description of the reactor.',
    'Reactor_Volume':'Volume in mL.',
    'Reactor_Atmosphere': 'Atmosphere in XX.',
    'Reactor_StirringSpeed': 'Stirring speed used in rpm.',
    'Reactor_Mode': 'Complete with the following options: chemostat/batch/fed-batch.',
    'Reactor_ContainersNumber' : 'Complete with the number of containers.',
    'Media_Name': 'Name of the media.',
    'Media_Path': 'Give the complete path to the file that describe your media.',
    'Bacteria_Genus_1':'Give the exact Genus of your bacteria strain.',
    'Bacteria_Species_1': 'Give the exact Species of your bacterial strain.',
    'Bacteria_NCBISpeciesID_1': 'Give the species NCBI ID of your bacterial strain.',
    'Bacteria_Strain_1':'Give the exact strain name of your bacteria.',
    'Bacteria_NCBIStrainID_1': 'Give the strai NCBI ID of your bacteria.',
    'Bacteria_GeneticallyModified_1': 'Fill in with 1 if mutant, 0 Otherwise.',
    'Blank':'Fill in with 1 if the biological replicate is blank. 0 otherwise. DO NOT leave in blank.',
    'Inoculum_Concentration': 'Indicated in cells per mL.',
    'Inoculum_Volume': 'Indicated in mL.',
    'Initial_pH' : 'Complete with the initial pH.',
    'Initial_Temperature': 'Initial temperature in Celsius.',
    'Carbon_Sourced': 'Fill in with 1 if carbon sourced. 0 otherwise. DO NOT leave in blank.',
    'Antibiotic': 'Fill in with 1 if antibiotic present. 0 otherwise. DO NOT leave in blank.',
    'Plate_Number': 'Number of plate.',
    'Plate_Position': 'List of locations in the plate, i.e: 1A, 1B, 2C.',
    'Files_Directory' : 'Comma separated list of directories. Keep the order as the plate positions.',
    'Perturbation_Property' : 'Indicate which property has been perturbed.',
    'Perturbation_Description' : 'Description of the perturbation.',
    'Perturbation_NewValue' : 'New value of the perturbed property.',
    'Perturbation_StartTime' : 'Time in minutes.',
    'Perturbation_EndTime':'Time in minutes.',
    'Perturbation_Plate_Number' : 'Number of plate perturbed',
    'Perturbation_Plate_Position' :'List of locations in the plate, i.e: 1A, 1B, 2C',
    'Perturbation_FilesDirectory': 'Comma separated list of directories. Keep the order as the plate positions.'
}

# Add headers and descriptions to the first row and modify the width of each columns
for col_idx, (header, description) in enumerate(headers.items(), start=1):
    cell = ws.cell(row=1, column=col_idx, value=header)
    cell.comment = Comment(description, author="ExcelBot")
    cell.font = Font(bold=True)  # Make the header bold

    # Calculate column width based on the length of the header text
    column_width = len(header)
    column_letter = get_column_letter(col_idx)
    ws.column_dimensions[column_letter].width = column_width +  3 #Gives extra space

# saves excel file in the locl directory
template_filename = LOCAL_DIRECTORY + 'submission_excel_template.xlsx'
wb.save(template_filename)

import yaml
import validators
import pandas as pd
import numpy as np
from parse_ex_to_yaml import NUM_ROWS1, NUM_ROWS2
from constants import LOCAL_DIRECTORY
template_filename_yaml = LOCAL_DIRECTORY + 'submission_yaml.yaml'
template_filename_yaml2 = LOCAL_DIRECTORY + 'submission_yaml2.yaml'


def load_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)
    

def test_study_format(data):
    df = pd.DataFrame(data['Study'])
    assert df['Study_Name'].apply(isinstance, args=(str,)).all(), "Study_Name must be a string"
    assert df['Study_Description'].apply(isinstance, args=(str,)).all(), "Study_Description must be a string"
    assert df['Study_PublicationURL'].apply(validators.url).all(), "Study_PublicationURL must be a valid URL"
    #STUDY_ID MISSING DEPENDING ON HOW THE ID is going to be

def test_bioreplicate_format(data):
    df = pd.DataFrame(data['BiologicalReplicate'])
    assert df['Antibiotic'].isin([0, 1]).all(), "Antibiotic must be 0 or 1"
    assert df['BiologicalReplicate_Description'].apply(isinstance, args=(str,)).all(), "BiologicalReplicate_Description must be a string"
    assert df['Blank'].isin([0, 1]).all(), "Blank must be a 0 or 1"
    assert df['Carbon_Sourced'].isin([0, 1]).all(), "Carbon_Sourced must be a 0 or 1"
    assert df['Comunity_Groups'].apply(isinstance, args=(str,)).all(), "Comunity_Groups must be a string"
    assert df['Files_Directory'].apply(isinstance, args=(str,)).all(), "Files_Directory must be a path"
    assert df['Initial_Temperature'].apply(lambda x: isinstance(x, (int, float))).all(), "Initial_Temperature must be numerical value"
    assert np.logical_and(df['Initial_pH'].between(0, 14), df['Initial_pH'].apply(lambda x: isinstance(x, (int, float)))).all(), "Initial_pH must be numerical value within 0 and 14"
    assert df['Inoculum_Concentration'].apply(lambda x: isinstance(x, (int, float))).all(), "Inoculum_Concentration must be numerical value"
    assert df['Inoculum_Volume'].apply(lambda x: isinstance(x, (int, float))).all(), "Inoculum_Volume must be numerical value"
    assert df['Media_Name'].apply(isinstance, args=(str,)).all(), "Media_Name must be a string"
    assert df['Media_Path'].apply(isinstance, args=(str,)).all(), "Media_Path must be a path"
    assert df['Media_Recipe'].apply(validators.url).all(), "Media_Recipe must be a valid URL"
    assert df['Plate_Number'].apply(isinstance, args=(int,)).all(), "Plate_Number must be numerical integer value"
    assert df['Plate_Position'].apply(isinstance, args=(str,)).all(), "Plate_Position must be a string"
    assert df['Reactor_ContainersNumber'].apply(isinstance, args=(int,)).all(), "Reactor_ContainersNumber must be numerical integer value"
    assert df['Reactor_Description'].apply(isinstance, args=(str,)).all(), "Reactor_Description must be a string"
    assert df['Reactor_Mode'].isin(["chemostat", "batch","fed-batch"]).all(), "Reactor_Mode must be chemostat/batch/fed-batch"
    assert df['Reactor_Name'].apply(isinstance, args=(str,)).all(), "Reactor_Name must be a string"
    assert df['Reactor_Pressure'].apply(lambda x: isinstance(x, (int, float))).all(), "Reactor_Pressure must be numerical value"
    assert df['Reactor_StirringMode'].isin(["linear", "orbital","vibrational"]).all(), "Reactor_StirringMode must be a linear/orbital//vibrational"
    assert df['Reactor_StirringSpeed'].apply(lambda x: isinstance(x, (int, float))).all(), "Reactor_StirringSpeed must be numerical value"
    assert df['Reactor_Volume'].apply(lambda x: isinstance(x, (int, float))).all(), "Reactor_Volume must be numerical value"
    

def test_bacteria_format(data):
    df = pd.DataFrame(data['Bacteria'])
    assert df['Bacteria_GeneticallyModified'].isin([0, 1]).all(), "Bacteria_GeneticallyModified must be 0 or 1"
    assert df['Bacteria_Genus'].apply(isinstance, args=(str,)).all(), "Bacteria_Genus must be a string"
    assert df['Bacteria_NCBISpeciesID'].apply(isinstance, args=(int,)).all(), "Bacteria_NCBISpeciesID must be numerical integer value"
    assert df['Bacteria_NCBIStrainID'].apply(isinstance, args=(int,)).all(), "Bacteria_NCBIStrainID must be numerical integer value"
    assert df['Bacteria_Species'].apply(isinstance, args=(str,)).all(), "Bacteria_Species must be a string"
    assert df['Bacteria_Strain'].apply(isinstance, args=(str,)).all(), "Bacteria_Strain must be a string"
    df2 = pd.DataFrame(data['Comunity'])
    assert df2['Comunity_ID'].apply(isinstance, args=(str,)).all(), "Comunity_ID must be a string"
    
data_yaml = load_yaml(template_filename_yaml)
data_yaml2=load_yaml(template_filename_yaml2)
test_study_format(data_yaml)
test_bioreplicate_format(data_yaml)
test_bacteria_format(data_yaml2)
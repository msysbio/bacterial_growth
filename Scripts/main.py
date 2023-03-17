import os
import argparse
import mysql.connector
import re

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import utils as ut
import db_functions as db

parser = argparse.ArgumentParser()
parser.add_argument('dir', type=ut.dir_path)
args = parser.parse_args()

PROJECT_DIRECTORY = '/Users/julia/bacterialGrowth_thesis/'
LAB_ANALYSIS_FILE = 'Scripts/Lab_files_analysis.sh'

HEADERS_FILE = 'IntermediateFiles/lab_headers.txt'
EXPERIMENTS_LIST = 'IntermediateFiles/listOfFiles.list'

EXP_DESCRIPTION = 'This experiment was done in Brussels.'
CULT_DESCRIPTION = 'In this perturbation, we kept pH at 5'
REP_DESCRIPTION = 'Replicate number #'

# ===========================================================================================
# All the above variables, most of them will be taken form the parser.
# ===========================================================================================

experimentDir = os.path.abspath(args.dir) + '/'
labAnalysisFile = PROJECT_DIRECTORY + LAB_ANALYSIS_FILE

# Analyse the provided files and get the necessary information from them
ut.runBash(labAnalysisFile, [PROJECT_DIRECTORY, experimentDir])
headers_dict = ut.clusterHeaders(PROJECT_DIRECTORY + HEADERS_FILE)

experimentName = [x.split(' ')[1] for x in open(PROJECT_DIRECTORY + 'IntermediateFiles/experiments_info.txt').readlines()][1]

experimentFiles = open(PROJECT_DIRECTORY + EXPERIMENTS_LIST, "r").readlines()
experimentFiles = list(map(lambda s: s.strip(), experimentFiles))



## Create new experiment with new cultivation conditions
expId = db.addExperiment(experimentName=experimentName)
number_cult = db.countRecords('CultivationConditions', 'experimentId', str(expId))
cultId = expId*100 + number_cult + 1
db.addCultivation(str(cultId), CULT_DESCRIPTION, str(expId))
number_rep = db.countRecords('TechnicalReplicates', 'cultivationId', str(cultId))


for i, f in enumerate(experimentFiles):
    repId = str(cultId) + '_' + str(number_rep + i + 1)
    db.addReplicate(str(repId), REP_DESCRIPTION, str(cultId))
    
    #Get directory of the provided paths
    path_end = max(ut.findOccurrences(f, "/"))
    path = f[:path_end+1]

    #Read file with all the data
    df = pd.read_table(f, sep=" ")
    
    growth_data = df[df.columns.intersection(headers_dict['abundance'])]
    growth_data = growth_data.round({'OD': 3})
    
    ph_data = df[df.columns.intersection(headers_dict['ph'])]
    ph_data = ph_data.round({'pH': 3})

    metabolites_data = df[df.columns.intersection(headers_dict['metabolites'])]
    
    # If len(df.columns) <= 1 (only time column), we do not save it
    if len(growth_data.columns) > 1:
        g_path = path+'abundance_file.txt'
        growth_data.to_csv(g_path, sep=" ", index=False)
        db.addReplicateFile(repId,bacterialAbundanceFile=g_path)
    
    if len(ph_data.columns) > 1:    
        p_path = path+'pH_file.txt'
        ph_data.to_csv(p_path, sep=" ", index=False)
        db.addReplicateFile(repId,phFile=p_path)
    
    if len(metabolites_data.columns) > 1:
        m_path = path+'metabolites_file.txt'
        metabolites_data.to_csv(m_path, sep=" ", index=False)
        db.addReplicateFile(repId,metabolitesFile=m_path)
    
    
    




    
    
    
    

    
    
    

    q = f""" INSERT IGNORE INTO TechnicalReplicates (bacterialAbundanceFile)
        VALUES ('{path+'abundance_file.txt'}')
        """


    q = f""" INSERT IGNORE INTO TechnicalReplicates (metabolitesFile)
        VALUES ('{path+'metabolites_file.txt'}')
        """

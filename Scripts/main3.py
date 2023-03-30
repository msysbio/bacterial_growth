import os
import re
from prettytable import PrettyTable

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from parser import bacterial_parser
from utils import (
    runBash, 
    getMatchingList
)
from populate import (
    addExperiment,
    addCultivation,
    addReplicates
)
from read_yml import (
    createStudyYml, createExperimentYml, createPerturbationYml
)
from github_download import getFile
import db_functions as db
# ===========================================================================================
# Variables:
# ===========================================================================================

PROJECT_DIRECTORY = '/Users/julia/bacterialGrowth_thesis/'
LAB_ANALYSIS_FILE = 'Scripts/Lab_files_analysis2.sh'

HEADERS_FILE = 'IntermediateFiles/lab_headers.txt'
EXPERIMENTS_LIST = 'IntermediateFiles/listOfFiles.list'

# Will come form the parser
EXP_DESCRIPTION = 'This experiment was done in Brussels.'
CULT_DESCRIPTION = 'In this perturbation, we kept pH at 5'
REP_DESCRIPTION = 'Replicate number #'

# ===========================================================================================
# ===========================================================================================

def main():

    args = bacterial_parser()

    num_studies = args.num_studies
    num_experiments = args.num_experiments
    num_perturbations = args.num_perturbations

    files_dir = args.files_dir

    if num_studies == None: num_studies = 0
    if num_experiments == None: num_experiments = 0
    if num_perturbations == None: num_perturbations = 0

    if num_studies > 1:
        print('\n\tYou can only introduce one experiment at a time\n')
    
    if num_studies == 1:
        if num_experiments == 0 and num_perturbations > 0:
            print('\n\tYou introduced NON-VALID parameters\n\tIf you want to introduce perturbations in a new study, you should also introduce the experiment info. \n\tIf you want to introduce perturbations into an existing experiment, and hence, into an existing study, you should only take the -p/--perturbations flag\n')
        else:
            createStudyYml(num_experiments, num_perturbations, files_dir)

    elif num_experiments > 0:
        print('\n You have to choose a study in which your experiments (and perturbations if indicated) will be added:')
        studies = db.getAllStudies()
        
        studies_table = PrettyTable()
        studies_table.field_names = ["ID", "Description"]
        for study in studies:
            studies_table.add_row(study)
        studies_table.align["Description"] = "l"
        print(studies_table)    
    
        study_id = input("\n-- Choose study ID: ")
        createExperimentYml(study_id, num_experiments, num_perturbations, files_dir)

    
    else:
        print('\n You have to choose a study and experiment in which your replicates files (and perturbations if indicated) will be added:')
        studies = db.getAllStudies()

        studies_table = PrettyTable()
        studies_table.field_names = ["ID", "Description"]
        for study in studies:
            studies_table.add_row(study)
        studies_table.align["Description"] = "l"
        print(studies_table)    
    
        study_id = input("\n-- Choose study ID: ")

        experiments = db.getAllExperiments(study_id)

        experiments_table = PrettyTable()
        experiments_table.field_names = ["ID","Study ID","Precultivation","Reactor","Plate ID","Column","Row","Media","Blank","inoculumConcentration","inoculumVolume","initialPh","initialTemperature","carbonSource","antibiotic","experimentDescription"]
        for experiment in experiments:
            experiments_table.add_row(experiment)
        # experiments_table.align["Description"] = "l"
        print(experiments_table)    

        experiment_id = input("\n-- Choose experiment ID: ")
        createPerturbationYml(study_id, experiment_id, num_perturbations, files_dir)
    

if __name__ == "__main__":
    main()
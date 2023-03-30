import os
import re
from prettytable import PrettyTable

from parser import bacterial_parser

from yml_functions import (
    createStudyYml, createExperimentYml, createPerturbationYml
)
import db_functions as db
# ===========================================================================================
# Variables:
# ===========================================================================================

# PROJECT_DIRECTORY = '/Users/julia/bacterialGrowth_thesis/'
# LAB_ANALYSIS_FILE = 'Scripts/Lab_files_analysis2.sh'

# HEADERS_FILE = 'IntermediateFiles/lab_headers.txt'
# EXPERIMENTS_LIST = 'IntermediateFiles/listOfFiles.list'

# # Will come form the parser
# EXP_DESCRIPTION = 'This experiment was done in Brussels.'
# CULT_DESCRIPTION = 'In this perturbation, we kept pH at 5'
# REP_DESCRIPTION = 'Replicate number #'

# ===========================================================================================
# ===========================================================================================

def prepare_populate(args):

    files_dir = os.path.abspath(args.files_dir) + '/'

    num_studies = args.num_studies
    num_experiments = args.num_experiments
    num_perturbations = args.num_perturbations

    if num_studies == None: num_studies = 0
    if num_experiments == None: num_experiments = 0
    if num_perturbations == None: num_perturbations = 0

    if num_studies > 1:
        print('\n\tERROR: You can only introduce one experiment at a time\n')
    
    if num_studies == 1:
        if num_experiments == 0 and num_perturbations > 0:
            print('\n\tERROR: You introduced NON-VALID parameters\n\tIf you want to introduce perturbations in a new study, you should also introduce the experiment info. \n\tIf you want to introduce perturbations into an existing experiment, and hence, into an existing study, you should only take the -p/--perturbations flag\n')
        else:
            createStudyYml(num_experiments, num_perturbations, files_dir)

    elif num_experiments > 0:
        print('\nYou have to choose a study in which your experiments (and perturbations if indicated) will be added:')
        studies = db.getAllStudies()

        if len(studies) == 0:
            print('\n\tERROR: There are no studies yet in the DB')
            print('\t- Create an study using the flag -s.\n')
            exit()
        
        studies_table = PrettyTable()
        studies_table.field_names = ["ID", "Description"]
        studies_table.align["Description"] = "l"

        studies_id = []
        for study in studies:
            studies_table.add_row(study)
            studies_id.append(str(study[0]))
        
        print(studies_table)
    
        study_id = input("-- Choose study ID: ")
        if study_id not in studies_id:
            print('\n\tERROR: You have not selected a valid study ID. Check the table above.\n')
            exit()
        
        createExperimentYml(study_id, num_experiments, num_perturbations, files_dir)

    
    else:
        print('\nYou have to choose a study and experiment in which your replicates files (and perturbations if indicated) will be added:')
        studies = db.getAllStudies()
        
        if len(studies) == 0:
            print('\n\tThere are no studies yet in the DB')
            print('\t- Create an study using the flag -s.\n')
            exit()
        
        studies_table = PrettyTable()
        studies_table.field_names = ["ID", "Description"]
        studies_table.align["Description"] = "l"

        studies_id = []
        for study in studies:
            studies_table.add_row(study)
            studies_id.append(str(study[0]))
        
        print(studies_table)
    
        study_id = input("-- Choose study ID: ")
        if study_id not in studies_id:
            print('\n\tERROR: You have not selected a valid study ID. Check the table above.\n')
            exit()

        experiments = db.getAllExperiments(study_id)

        if len(experiments) == 0:
            print('\n\tERROR: There are no experiments with id {}:'.format(study_id))
            print('\t- Select another study ID\n\t- Create experiments with this study ID before introducing perturbations/replicates files into it.\n')
            exit()

        experiments_table = PrettyTable()
        experiments_table.field_names = ["ID","Study ID","Precult","Reactor","Plate ID","Column","Row","Media","Blank","inoculumConc","inoculumVol","initPh","initTemp","carbonSource","antibiotic","Description"]
        
        experiments_id = []
        for experiment in experiments:
            experiments_table.add_row(experiment)
            experiments_id.append(str(experiment[0]))
        
        print(experiments_table)    

        experiment_id = input("-- Choose experiment ID: ")
        if experiment_id not in experiments_id:
            print('\n\tERROR: You have not selected a valid experiment ID. Check the table above.\n')
            exit()

        createPerturbationYml(study_id, experiment_id, num_perturbations, files_dir)
    
    print('Go to yml_info_files/ and complete the created file with the information you want to introduce in the DB.\n\n')
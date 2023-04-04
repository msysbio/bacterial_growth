import os
from prettytable import PrettyTable

from yml_functions import createStudyYml, createExperimentYml, createPerturbationYml, createReplicatesYml
import db_functions as db
from bash_functions import runBash

PROJECT_DIRECTORY = '/Users/julia/bacterialGrowth_thesis/'
MODIFY_YML_FILE = 'src/bash_scripts/modify_yml_files.sh'
modifyYml = PROJECT_DIRECTORY + MODIFY_YML_FILE

def prepare_populate(args):

    # files_dir = os.path.abspath(args.files_dir) + '/'

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
            createStudyYml(num_experiments, num_perturbations)
            runBash(modifyYml, ['yml_info_files/study_information_tmp.yml', 'yml_info_files/study_information.yml'])

    elif num_experiments > 0:
        print('\nYou have to choose a study in which your experiments (and perturbations if indicated) will be added:')
        # ==========================================================================================
        studies = db.getAllRecords('Study')

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
        
        createExperimentYml(study_id, num_experiments, num_perturbations)
        runBash(modifyYml, ['yml_info_files/experiment_information_tmp.yml', 'yml_info_files/experiment_information.yml'])

    
    elif num_perturbations > 0:
        print('\nYou have to choose a study and experiment in which your perturbations will be added:')
        # ==========================================================================================
        studies = db.getAllRecords('Study')
        
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

        # ==========================================================================================
        experiments = db.getAllRecords('Experiment', studyId=study_id)

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

        # createPerturbationYml(study_id, experiment_id, num_perturbations, files_dir)
        createPerturbationYml(study_id, experiment_id, num_perturbations)
        runBash(modifyYml, ['yml_info_files/perturbation_information_tmp.yml', 'yml_info_files/perturbation_information.yml'])
        


    else:
        print('\nYou have to choose a study, experiment and perturbation in which your replicates files will be added:')
        # ==========================================================================================
        studies = db.getAllRecords('Study')
        
        if len(studies) == 0:
            print('\n\tThere are no studies yet in the DB')
            print('\t- Create an study using the flag -s.\n')
            exit()
        
        studies_table = PrettyTable()
        studies_table.field_names = ["ID", "Name", "Description"]
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

        # ==========================================================================================
        experiments = db.getAllRecords('Experiment', studyId=study_id)

        if len(experiments) == 0:
            print('\n\tERROR: There are no experiments with study id {}:'.format(study_id))
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

        # ==========================================================================================
        perturbations = db.getAllRecords('Perturbation', experimentId=experiment_id)

        if len(perturbations) == 0:
            print('\n\tERROR: There are no perturbations with experiment id {}:'.format(experiment_id))
            print('\t- Select another experiment ID\n\t- Create perturbation with this experiment ID before introducing replicates files into it.\n')
            exit()

        perturbations_table = PrettyTable()
        perturbations_table.field_names = ["ID","Experiment ID","Property","New Value","Starting time (min)","Ending time (min)","Description"]
        
        perturbations_id = []
        for perturbation in perturbations:
            perturbations_table.add_row(perturbation)
            perturbations_id.append(str(perturbation[0]))
        
        print(perturbations_table)    

        perturbation_id = input("-- Choose perturbation ID: ")
        if perturbation_id not in perturbations_id:
            print('\n\tERROR: You have not selected a valid perturbation ID. Check the table above.\n')
            exit()
        
        # createPerturbationYml(study_id, experiment_id, num_perturbations, files_dir)
        createReplicatesYml(study_id, experiment_id, perturbation_id)
        runBash(modifyYml, ['yml_info_files/replicates_information_tmp.yml', 'yml_info_files/replicates_information.yml'])
    
    print('Go to yml_info_files/ and complete the created file with the information you want to introduce in the DB.\n\n')
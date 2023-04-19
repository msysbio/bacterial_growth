import os
from prettytable import PrettyTable

from yml_functions import createStudyYml, createExperimentYml, createPerturbationYml, createReplicatesYml
from bash_functions import runBash
from user_inputs import *

PROJECT_DIRECTORY = '/Users/julia/bacterialGrowth_thesis/'
MODIFY_YML_FILE = 'src/bash_scripts/modify_yml_files.sh'
modifyYml = PROJECT_DIRECTORY + MODIFY_YML_FILE

def create_yml_file(args):

    num_studies = args.num_studies
    num_experiments = args.num_experiments
    num_perturbations = args.num_perturbations

    if num_studies == None: num_studies = 0
    if num_experiments == None: num_experiments = 0
    if num_perturbations == None: num_perturbations = 0

    if num_studies > 1:
        print('\n\tERROR: You can only introduce one experiment at a time\n')
        exit()
    
    if num_studies == 1:
        if num_experiments == 0 and num_perturbations > 0:
            print('\n\tERROR: You introduced NON-VALID parameters\n\tIf you want to introduce perturbations in a new study, you should also introduce the experiment info. \n\tIf you want to introduce perturbations into an existing experiment, and hence, into an existing study, you should only take the -p/--num_perturbations flag. \n\tIf you want to create a new experiment, you should also take the -e/--num_experiments flag\n')
        else:
            createStudyYml(num_experiments, num_perturbations)
            runBash(modifyYml, ['yml_info_files/study_information_tmp.yml', 'yml_info_files/study_information.yml'])

    elif num_experiments > 0:
        study_id = chooseStudy()
        
        createExperimentYml(study_id, num_experiments, num_perturbations)
        runBash(modifyYml, ['yml_info_files/experiment_information_tmp.yml', 'yml_info_files/experiment_information.yml'])

    
    elif num_perturbations > 0:
        study_id = chooseStudy()
        experiment_id = chooseExperiment(study_id)
        
        createPerturbationYml(study_id, experiment_id, num_perturbations)
        runBash(modifyYml, ['yml_info_files/perturbation_information_tmp.yml', 'yml_info_files/perturbation_information.yml'])
        

    else:
        study_id = chooseStudy()
        experiment_id = chooseExperiment(study_id)
        perturbation_id = choosePerturbation(experiment_id)
        
        createReplicatesYml(study_id, experiment_id, perturbation_id)
        runBash(modifyYml, ['yml_info_files/replicates_information_tmp.yml', 'yml_info_files/replicates_information.yml'])
    
    print('Go to yml_info_files/ and complete the created file with the information you want to introduce in the DB.\n\n')
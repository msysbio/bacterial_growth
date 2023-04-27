from yml_functions import createStudyYml, createBiologicalReplicateYml, createPerturbationYml, createReplicatesYml
from bash_functions import runBash
from user_inputs import *
from constants import *

def create_yml_file(args):
    '''
    Create yml file with user instructions

    :param args: user input
    '''

    yml_files_dir = LOCAL_DIRECTORY+'yml_files/'
    modifyYml = PROJECT_DIRECTORY + MODIFY_YML_FILE

    num_studies = args.num_studies
    num_biological_replicates = args.num_biological_replicates
    num_perturbations = args.num_perturbations

    if num_studies == None: num_studies = 0
    if num_biological_replicates == None: num_biological_replicates = 0
    if num_perturbations == None: num_perturbations = 0

    if num_studies > 1:
        print('\n\tERROR: You can only introduce one study at a time\n')
        exit()
    
    if num_studies == 1:
        if num_biological_replicates == 0 and num_perturbations > 0:
            print('\n\tERROR: You introduced NON-VALID parameters\n\tIf you want to introduce perturbations in a new study, you should also introduce the biological replicate info. \n\tIf you want to introduce perturbations into an existing biological replicate, and hence, into an existing study, you should only take the -p/--num_perturbations flag. \n\tIf you want to create a new biological replicate, you should also take the -e/--num_biological_replicates flag\n')
        else:
            createStudyYml(num_biological_replicates, num_perturbations)
            runBash(modifyYml, [yml_files_dir+'study_information_tmp.yml', yml_files_dir+'study_information.yml'])
            print('\n\nstudy_information.yml created!')

    elif num_biological_replicates > 0:
        study_id = chooseStudy()
        
        createBiologicalReplicateYml(study_id, num_biological_replicates, num_perturbations)
        runBash(modifyYml, [yml_files_dir+'biological_replicate_information_tmp.yml', yml_files_dir+'biological_replicate_information.yml'])
        print('\n\nbiological_replicate_information.yml created!')

    
    elif num_perturbations > 0:
        study_id = chooseStudy()
        biological_id = chooseBiologicalReplicate(study_id)
        
        createPerturbationYml(study_id, biological_id, num_perturbations)
        runBash(modifyYml, [yml_files_dir+'perturbation_information_tmp.yml', yml_files_dir+'perturbation_information.yml'])
        print('\n\nperturbation_information.yml created!')
        

    else:
        study_id = chooseStudy()
        biological_id = chooseBiologicalReplicate(study_id)
        perturbation_id = choosePerturbation(biological_id)

        if perturbation_id == '0':
            createReplicatesYml(study_id, biological_id, perturbation_id=None)    
        else:
            createReplicatesYml(study_id, biological_id, perturbation_id)
        runBash(modifyYml, [yml_files_dir+'replicates_information_tmp.yml', yml_files_dir+'replicates_information.yml'])
        print('\n\replicates_information.yml created!')
    
    
    print('Go to yml_info_files/ and complete the created file with the information you want to introduce in the DB.\n\n')
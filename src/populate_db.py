import db_functions as db
from yml_functions import (read_yml)

def populate_db(args):

    info_file = args.info_file
    info = read_yml(info_file)

    if 'STUDY_DESCRIPTION' in info:
        study_id = db.addStudy()
    else:
        study_id = info['STUDY_ID']
    
    if 'EXPERIMENT' in info:
        exp_id = db.addExperiment()
    else:
        exp_id = info['EXPERIMENT_ID']

    if 'PERTURBATION' in info:
        pert_id = db.addPerturbation()
        


    return False
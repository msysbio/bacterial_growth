from prettytable import PrettyTable
import db_functions as db

def chooseStudy():
    print('\nYou have to choose a study in which your experiments (and perturbations if indicated) will be added:')
    # ==========================================================================================
    studies = db.getAllRecords('Study')

    if len(studies) == 0:
        print('\n\tERROR: There are no studies yet in the DB')
        print('\t- Create an study using the flag -s.\n')
        exit()
    
    studies_table = PrettyTable()
    studies_table.field_names = ["ID", "Name", "Description"]
    studies_table.align["Name"] = "l"
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
    
    return study_id

def chooseExperiment(study_id):
    experiments = db.getAllRecords('Experiment', studyId=study_id)
     
    if len(experiments) == 0:
        print('\n\tERROR: There are no experiments with id {}:'.format(study_id))
        print('\t- Select another study ID\n\t- Create experiments with this study ID before introducing perturbations/replicates files into it.\n')
        exit()

    experiments_table = PrettyTable()
    experiments_table.field_names = ["ID","Name","Study ID","Precult","Reactor","Plate ID","Column","Row","Media","Blank","inoculumConc","inoculumVol","initPh","initTemp","carbonSource","antibiotic","Description"]
    
    experiments_id = []
    for experiment in experiments:
        experiments_table.add_row(experiment)
        experiments_id.append(str(experiment[0]))
    
    print(experiments_table)    

    experiment_id = input("-- Choose experiment ID: ")
    if experiment_id not in experiments_id:
        print('\n\tERROR: You have not selected a valid experiment ID. Check the table above.\n')
        exit()

    return experiment_id

def choosePerturbation(experiment_id):
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

    return perturbation_id

def chooseReplicate(experiment_id, perturbation_id):
    if perturbation_id == None:
        id = experiment_id
        replicates = db.getAllRecords('TechnicalReplicate', experimentId=id)
        if len(replicates) == 0:
            print('\n\tERROR: There are no replicates with experiment_id {}'.format(id))
            print('\t- Select another experiment ID\n\t- Create perturbation with this experiment ID before introducing replicates files into it.\n')
            exit()

    else:
        id = perturbation_id
        replicates = db.getAllRecords('TechnicalReplicate', perturbationId=id)
        if len(replicates) == 0:
            print('\n\tERROR: There are no replicates with perturbation_id {}'.format(id))
            print('\t- Select another experiment ID\n\t- Create perturbation with this experiment ID before introducing replicates files into it.\n')
            exit()

    replicates_table = PrettyTable()
    replicates_table.field_names = ["ID","Experiment ID","Perturbation ID"]
    
    replicates_id = []
    for replicate in replicates:
        print(replicate[0:3])
        replicates_table.add_row(replicate[0:3])
        replicates_id.append(str(replicate[0]))
    
    print(replicates_table)    

    replicate_id = input("-- Choose replicate ID: ")
    if replicate_id not in replicates_id:
        print('\n\tERROR: You have not selected a valid replicate ID. Check the table above.\n')
        exit()

    return replicate_id
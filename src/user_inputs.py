from prettytable import PrettyTable
import db_functions as db

def chooseStudy():
    '''
    Print the existing study and waits a user input
    
    :return study_id
    '''
    studies = db.getAllRecords('Study', {})

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
    '''
    Print the existing experiments with study_id and waits a user input
    
    :param study_id
    :return experiment_id
    '''
    experiments = db.getAllRecords('Experiment', {'studyId':study_id})
     
    if len(experiments) == 0:
        print('\n\tERROR: There are no experiments with id {}:'.format(study_id))
        print('\t- Select another study ID\n\t- Create experiments with this study ID before introducing perturbations/replicates files into it.\n')
        exit()

    experiments_table = PrettyTable()
    experiments_table.field_names = ["ID","Name","Study ID","Precult","Reactor","Media","Blank","inoculumConc","inoculumVol","initPh","initTemp","carbonSource","antibiotic"]

    experiments_id = []
    for experiment in experiments:
        difference_result = [item for item in [*range(0, len(experiment))] if item not in [5, 6, 7, 16]]
        experiment_tuple = tuple(experiment[i] for i in difference_result)
        experiments_table.add_row(experiment_tuple)
        experiments_id.append(str(experiment[0]))
    
    print(experiments_table)

    experiment_id = input("-- Choose experiment ID: ")
    if experiment_id not in experiments_id:
        print('\n\tERROR: You have not selected a valid experiment ID. Check the table above.\n')
        exit()

    return experiment_id

def choosePerturbation(experiment_id):
    '''
    Print the existing experiments with study_id and waits a user input
    
    :param study_id
    :return experiment_id
    '''
    perturbations = db.getAllRecords('Perturbation', {'experimentId':experiment_id})

    if len(perturbations) == 0:
        print('\n\tThere are no perturbations with experiment id {}:'.format(experiment_id), '=> check for technical replicates')
        perturbation_id = 0
        return perturbation_id

    perturbations_table = PrettyTable()
    perturbations_table.field_names = ["ID","Experiment ID","Property","New Value","Starting time (min)","Ending time (min)","Description"]
    
    perturbations_id = []
    for perturbation in perturbations:
        difference_result = [item for item in [*range(0, len(perturbation))] if item not in [2,3,4]]
        perturbation_tuple = tuple(perturbation[i] for i in difference_result)
        perturbations_table.add_row(perturbation_tuple)
        perturbations_id.append(str(perturbation[0]))
    
    print(perturbations_table)    
    print("If you do not want to choose any perturbation, press 0")
    
    perturbation_id = input("-- Choose perturbation ID: ")
    if perturbation_id not in perturbations_id and perturbation_id != '0':
        print('\n\tERROR: You have not selected a valid perturbation ID. Check the table above.\n')
        exit()

    return perturbation_id

def chooseReplicate(experiment_id, perturbation_id):
    '''
    Print the existing replicates with experiment_id and perturbation_id and waits a user input
    
    :param experiment_id, perturbation_id
    :return replicate_id
    '''
    if perturbation_id == None:
        id = experiment_id
        replicates = db.getAllRecords('TechnicalReplicate', {'experimentId':id, 'perturbationID':'null'})
        if len(replicates) == 0:
            print('\n\tERROR: There are no replicates with experiment_id {}'.format(id))
            print('\t- Select another experiment ID\n\t- Create perturbation with this experiment ID before introducing replicates files into it.\n')
            exit()

    else:
        id = perturbation_id
        replicates = db.getAllRecords('TechnicalReplicate', {'perturbationId':id})
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

def choosePlotOption():
    '''Choose between the plotting options
    
    :return option
    '''
    print('Choose the plotting option:')
    print('\t1: Plot one technical replicate.')
    print('\t2: Plot mean and deviation from several replicates from the same perturbation/experiment.')
    print('\t3: Plot mean and deviation from several replicates from one experiment (with all its perturbations).')
    option = input("\n Option: ")
    return option
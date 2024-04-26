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

def chooseBiologicalReplicate(study_id):
    '''
    Print the existing biological replicates with study_id and waits a user input
    
    :param study_id
    :return biological_id
    '''
    biological_replicates = db.getAllRecords('BiologicalReplicate', {'studyId':study_id})
     
    if len(biological_replicates) == 0:
        print('\n\tERROR: There are no biological replicates with id {}:'.format(study_id))
        print('\t- Select another study ID\n\t- Create biological replicates with this study ID before introducing perturbations/replicates files into it.\n')
        exit()

    biological_replicates_table = PrettyTable()
    biological_replicates_table.field_names = ["ID","Name","Study ID","Precult","Reactor","Plate","Pos","Media","Blank","inoculumConc","inoculumVol","initPh","initTemp","carbonSource","antibiotic"]

    biological_replicates_id = []
    for biological_replicate in biological_replicates:
        difference_result = [item for item in [*range(0, len(biological_replicate))] if item not in [15]]
        biological_replicate_tuple = tuple(biological_replicate[i] for i in difference_result)
        biological_replicates_table.add_row(biological_replicate_tuple)
        biological_replicates_id.append(str(biological_replicate[0]))
    
    print(biological_replicates_table)

    biological_id = input("-- Choose biological replicate ID: ")
    if biological_id not in biological_replicates_id:
        print('\n\tERROR: You have not selected a valid biological replicate ID. Check the table above.\n')
        exit()

    return biological_id

def choosePerturbation(biological_id):
    '''
    Print the existing biological replicates with study_id and waits a user input
    
    :param study_id
    :return biological_id
    '''
    perturbations = db.getAllRecords('Perturbation', {'biologicalReplicateId':biological_id})

    if len(perturbations) == 0:
        print('\n\tThere are no perturbations with biological replicate id {}:'.format(biological_id), '=> check for technical replicates')
        perturbation_id = 0
        return perturbation_id

    perturbations_table = PrettyTable()
    perturbations_table.field_names = ["ID","BR ID","Plate","Pos","Property","New Value","Starting time (min)","Ending time (min)"]
    
    perturbations_id = []
    for perturbation in perturbations:
        difference_result = [item for item in [*range(0, len(perturbation))] if item not in [8]]
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

def chooseReplicate(biological_id, perturbation_id):
    print(biological_id, perturbation_id)
    '''
    Print the existing replicates with biological_id and perturbation_id and waits a user input
    
    :param biological_id, perturbation_id
    :return technical_id
    '''
    if perturbation_id == None:
        id = biological_id
        replicates = db.getAllRecords('TechnicalReplicate', {'biologicalReplicateId':id, 'perturbationID':'null'})
        if len(replicates) == 0:
            print('\n\tERROR: There are no replicates with biological_id {}'.format(id))
            print('\t- Select another biological replicate ID\n\t- Create perturbation with this biological replicate ID before introducing replicates files into it.\n')
            exit()

    else:
        id = perturbation_id
        replicates = db.getAllRecords('TechnicalReplicate', {'perturbationId':id})
        if len(replicates) == 0:
            print('\n\tERROR: There are no replicates with perturbation_id {}'.format(id))
            print('\t- Select another biological replicate ID\n\t- Create perturbation with this biological replicate ID before introducing replicates files into it.\n')
            exit()

    replicates_table = PrettyTable()
    replicates_table.field_names = ["ID","BiologicalReplicate ID","Perturbation ID"]
    
    replicates_id = []
    for replicate in replicates:
        print(replicate[0:3])
        replicates_table.add_row(replicate[0:3])
        replicates_id.append(str(replicate[0]))
    
    print(replicates_table)    

    technical_id = input("-- Choose replicate ID: ")
    if technical_id not in replicates_id:
        print('\n\tERROR: You have not selected a valid replicate ID. Check the table above.\n')
        exit()

    return technical_id

def choosePlotOption():
    '''Choose between the plotting options
    
    :return option
    '''
    print('Choose the plotting option:')
    print('\t1: Plot one technical replicate.')
    print('\t2: Plot mean and deviation from several replicates from the same perturbation/biological replicate.')
    print('\t3: Plot mean and deviation from several replicates from one biological replicate (with all its perturbations).')
    option = input("\n Option: ")
    return option
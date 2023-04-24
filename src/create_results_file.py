from zipfile import ZipFile
import pandas as pd
import db_functions as db
from utils import transformStringIntoList
from constants import *

# Bacteroides thetaiotaomicron, Faecalibacterium prausnitzii
# Glucose, Pyruvate

def getInformationFile(args):
    '''
    This function gets the user parameters to search into the db
    First, it calculates the query to run (so it first calculates the where arguments, join arguments...)
    It gets a list with the experiment ids that meet the requirements
    With this ids it builds a dictionary with the desired information with which a txt info file is written
    Everything is placed in a zip file
    '''
    metabolites_list = []
    join_args = []
    where_args = {}

    # get experimentId list
    if args.bacteria != None:
        if len(args.bacteria) == 1:
            bacteria_list = transformStringIntoList(args.bacteria[0], ',')
        elif len(args.bacteria) > 1:
            lst = ''
            for bct in args.bacteria: lst = lst + bct + ' '
            bacteria_list = transformStringIntoList(lst[:-1], ',')
    
        where_args['bacteriaSpecies'] = tuple(bacteria_list)
        join_args.append({'table_from': 'BacteriaCommunity', 'table_to': 'Bacteria', 'field': 'bacteriaId'})
        join_args.append({'table_from': 'BacteriaCommunity', 'table_to': 'Experiment', 'field': 'experimentId'})
    
    if args.metabolites != None:
        if len(args.metabolites) == 1:
            metabolites_list = transformStringIntoList(args.metabolites[0], ',')
        elif len(args.metabolites) > 1:
            lst = ''
            for met in args.metabolites: lst = lst + met + ' '
            metabolites_list = transformStringIntoList(lst[:-1], ',')

        where_args['metabolitesFile'] = 'not null'
        join_args.append({'table_from': 'Experiment', 'table_to': 'TechnicalReplicate', 'field': 'experimentId'})

    if 'bacteriaSpecies' in where_args:
        experiment_ids = getExperimentsWithBacteria(join_args, where_args)
    elif 'metabolitesFile' in where_args:
        experiment_ids = getExperimentsWithMetabolites(join_args, where_args)

    # get files from the experimentId list
    results_dict = writeResultsDictionary(experiment_ids, metabolites_list)
    # write the txt file and save into zip
    writeResultsTxt(results_dict)

def getExperimentsWithBacteria(join_args, where_args):
    '''
    This function builds the query if we look for specific bacteria

    args: join_args, to build the join clause with variable number of joins, and where_args, conditions to the query
    return: list with experiment ids
    '''
    field = 'BacteriaCommunity.experimentId'
    table = 'BacteriaCommunity'
    
    phrase = "SELECT "+field+" FROM "+table+" "
        
    # Join clause
    for arg in join_args:
        join_clause = db.getJoinClause(arg['table_from'], arg['table_to'], arg['field'])
        phrase = phrase+join_clause + " "
    
    # Where, groupby and having clauses
    where_clause = db.getWhereClause(where_args)
    groupby_clause = db.getGroupByClause(field)
    for key, val in where_args.items():
        if key == 'bacteriaSpecies':
            having_clause = db.getHavingClause('COUNT', key, '=', len(val), distinct=True)
    
    #Final query
    phrase = phrase +where_clause+" "+groupby_clause+" "+having_clause

    res = db.execute(phrase)
    return res

def getExperimentsWithMetabolites(join_args, where_args):
    '''
    This function builds the query if we look for metabolites files

    args: where_args, conditions to the query
    return: list with experiment ids
    '''
    field = 'Experiment.experimentId'
    table = 'Experiment'
    
    phrase = "SELECT DISTINCT "+field+" FROM "+table+" "
    
    for arg in join_args:
        join_clause = db.getJoinClause(arg['table_from'], arg['table_to'], arg['field'])
        phrase = phrase+join_clause + " "

    
    where_clause = db.getWhereClause(where_args)
    
    phrase = phrase +where_clause
    res = db.execute(phrase)
    
    return res

def writeResultsDictionary(identifiers, met_list):
    '''Builds the dictionary from the ids list'''
    dictionary = {}
    for experiment_id in identifiers:
        
        dictionary[experiment_id[0]] = {'metadata':{}}
        
        exp_metadata = db.getRecords('Experiment', exp_metadata_fields, {'experimentId':experiment_id[0]})
        exp_metadata_dict = dict(zip(exp_metadata_fields, exp_metadata[0]))
        dictionary[experiment_id[0]]['metadata'] = exp_metadata_dict
        
        perturbation_ids = db.getRecords('Perturbation', ['perturbationId'], {'experimentId':experiment_id[0]})
        
        if len(met_list) != 0:
            res = db.getFiles({'metabolitesFile'}, {'experimentId':experiment_id[0], 'perturbationId': 'null'})
            for i, files in enumerate(res):
                headers = pd.read_csv(files[0], sep=" ").columns
                if set(met_list).issubset(set(headers.tolist())):
                    id_args = {'experimentId':experiment_id[0], 'perturbationId': 'null'}
        else:
            id_args = {'experimentId':experiment_id[0], 'perturbationId': 'null'}
            
        files_res = db.getFiles(file_types, id_args)
        dictionary[experiment_id[0]]['0'] = {'files': ''}
        dictionary[experiment_id[0]]['0']['files'] = files_res
        
        # Each perturbations
        for perturbation_id in perturbation_ids:
            
            if len(met_list) != 0:
                res = db.getFiles({'metabolitesFile'}, {'experimentId':experiment_id[0], 'perturbationId': perturbation_id[0]})
                for i, files in enumerate(res):
                    headers = pd.read_csv(files[0], sep=" ").columns
                    if set(met_list).issubset(set(headers.tolist())):
                        id_args = {'experimentId':experiment_id[0], 'perturbationId': perturbation_id[0]}
            else:
                id_args = {'experimentId':experiment_id[0], 'perturbationId': perturbation_id[0]}
                
        
            files_res = db.getFiles(file_types, id_args)
            pert_metadata = db.getRecords('Perturbation', pert_metadata_fields, {'perturbationId':id_args['perturbationId']})
            pert_metadata_dict = dict(zip(pert_metadata_fields, pert_metadata[0]))

            dictionary[experiment_id[0]][perturbation_id[0]] = {'metadata': '', 'files': ''}
            dictionary[experiment_id[0]][perturbation_id[0]]['metadata'] = pert_metadata_dict
            dictionary[experiment_id[0]][perturbation_id[0]]['files'] = files_res
    
    return dictionary

def writeResultsTxt(dictionary):
    ''' Write txt and zip from the data dictionary'''
    with ZipFile(LOCAL_DIRECTORY+"000_myZip.zip", mode="w"):
        print('ZIP file created!')

    with open(LOCAL_DIRECTORY+'README.md', 'w') as out_file:
        for key, val in dictionary.items():
            experiment_id = key
            header = 'EXPERIMENT '+str(experiment_id)
            out_file.write('-'*80+'\n'+header+'\n'+'-'*80+'\n')
            
            for key2, val2 in dictionary[experiment_id].items():
                # Experiment metadata
                if key2 == 'metadata':
                    out_file.write('Metadata:\n')
                    lines = writeMetadataTxt(dictionary[experiment_id][key2], 'experiment')
                    out_file.write(lines)
                # Experiment perturbations
                else:
                    perturbation_id = key2
                    pert = 'Perturbation '+key2
                    out_file.write('\n'+pert+'\n'+'-'*80+'\n')

                    for key3, val3 in dictionary[experiment_id][perturbation_id].items():
                        # Perturbation metadata (if corresponds)
                        if key3 == 'metadata':
                            out_file.write('Metadata:\n')
                            lines = writeMetadataTxt(dictionary[experiment_id][perturbation_id]['metadata'], 'perturbation')
                            out_file.write(lines)
                        
                        # Perturbation files
                        if key3 == 'files':
                            out_file.write('Files:\n')
                            for file in dictionary[experiment_id][perturbation_id]['files']:
                                out_file.write('\t'+file[0]+'\n')
                                
                                # Save them in ZIP
                                with ZipFile(LOCAL_DIRECTORY+'000_myZip.zip', 'a') as archive:
                                    regex = PROJECT_DIRECTORY+'(.*)'
                                    file_mod = re.findall(regex, file[0])[0]
                                    print(file_mod)
                                    archive.write(file[0], file_mod)
            out_file.write('\n'*3)

    # Save README.md in ZIP
    with ZipFile(LOCAL_DIRECTORY+'000_myZip.zip', 'a') as archive:
        archive.write(LOCAL_DIRECTORY+'README.md', 'README.md')
        # archive.printdir()

def writeMetadataTxt(dict, type):
    ''' Writes the metadata part of the dictionary, as it is repeated several times'''
    if type == 'experiment':
        lines = '\tPlate id: '+str(dict['plateId'])+'\n'
        lines = lines + '\tPlate location: '+str(dict['plateColumn'])+dict['plateRow']+'\n'
        lines = lines + '\tInitial pH: '+str(dict['initialPh'])+'\n'
        lines = lines + '\tInitial temperature: '+str(dict['initialTemperature'])+'\n'
    elif type == 'perturbation':
        lines = '\tProperty perturbed: '+dict['property']+'\n'
        lines = lines + '\tNew value: '+str(dict['newValue'])+'\n'
        lines = lines + '\tStarting time (minutes): '+str(dict['startTime'])+'\n'
        lines = lines + '\tEnding time (minutes): '+str(dict['endTime'])+'\n'
    return lines
from zipfile import ZipFile
import pandas as pd
import db_functions as db
from utils import transformStringIntoList, getZipName
from constants import *

def getInformationFile(args):
    '''
    This function gets the user parameters to search into the db
    First, it calculates the query to run (so it first calculates the where arguments, join arguments...)
    It gets a list with the biological replicates ids that meet the requirements
    With this ids it builds a dictionary with the desired information with which a txt info file is written
    Everything is placed in a zip file

    :param: args from parser
    '''
    metabolites_list = []
    join_args = []
    where_args = {}

    # get biologicalReplicateId list
    if args.bacteria != None:
        if len(args.bacteria) == 1:
            bacteria_list = transformStringIntoList(args.bacteria[0], ',')
        elif len(args.bacteria) > 1:
            lst = ''
            for bct in args.bacteria: lst = lst + bct + ' '
            bacteria_list = transformStringIntoList(lst[:-1], ',')
    
        where_args['bacteriaSpecies'] = tuple(bacteria_list)
        join_args.append({'table_from': 'BacteriaCommunity', 'table_to': 'Bacteria', 'field': 'bacteriaId'})
        join_args.append({'table_from': 'BacteriaCommunity', 'table_to': 'BiologicalReplicate', 'field': 'biologicalReplicateId'})
    
    if args.metabolites != None:
        if len(args.metabolites) == 1:
            metabolites_list = transformStringIntoList(args.metabolites[0], ',')
        elif len(args.metabolites) > 1:
            lst = ''
            for met in args.metabolites: lst = lst + met + ' '
            metabolites_list = transformStringIntoList(lst[:-1], ',')

        where_args['metabolitesFile'] = 'not null'
        join_args.append({'table_from': 'BiologicalReplicate', 'table_to': 'TechnicalReplicate', 'field': 'biologicalReplicateId'})
    
    
    if 'bacteriaSpecies' in where_args:
        biological_ids = getBiologicalReplicatesWithBacteria(join_args, where_args)
    elif 'metabolitesFile' in where_args:
        biological_ids = getBiologicalReplicatesWithMetabolites(join_args, where_args)

    # get files from the biologicalReplicateId list
    results_dict = writeResultsDictionary(biological_ids, metabolites_list)
    # write the txt file and save into zip
    writeResultsTxt(results_dict)

def getBiologicalReplicatesWithBacteria(join_args, where_args):
    '''
    This function builds the query if we look for specific bacteria

    :param join_args where_args: args necessary for the db query
    :return: list with biological replicate ids
    '''
    field = 'BacteriaCommunity.biologicalReplicateId'
    table = 'BacteriaCommunity'
    
    phrase = "SELECT "+field+" FROM "+table+" "
        
    # Join clause
    for arg in join_args:
        join_clause = db.getJoinClause(arg['table_from'], arg['table_to'], arg['field'])
        phrase = phrase+join_clause + " "
    
    # Where, groupby and having clauses
    where_clause = db.getWhereInClause(where_args)
    groupby_clause = db.getGroupByClause(field)
    for key, val in where_args.items():
        if key == 'bacteriaSpecies':
            having_clause = db.getHavingClause('COUNT', key, '=', len(val), distinct=True)
    
    #Final query
    phrase = phrase +where_clause+" "+groupby_clause+" "+having_clause
    res = db.execute(phrase)
    return res

def getBiologicalReplicatesWithMetabolites(join_args, where_args):
    '''
    This function builds the query if we look for metabolites files

    :param join_args where_args: args necessary for the db query
    :return: list with biological replicate ids
    '''
    field = 'BiologicalReplicate.biologicalReplicateId'
    table = 'BiologicalReplicate'
    
    phrase = "SELECT DISTINCT "+field+" FROM "+table+" "
    
    for arg in join_args:
        join_clause = db.getJoinClause(arg['table_from'], arg['table_to'], arg['field'])
        phrase = phrase+join_clause + " "

    
    where_clause = db.getWhereInClause(where_args)
    
    phrase = phrase +where_clause
    res = db.execute(phrase)
    
    return res

def writeResultsDictionary(biological_ids, met_list):
    '''Builds the dictionary from the ids list
    
    :param biological_ids: ids of the results for the user input
    :param met_list: metabolites list in case indicated by the user
    :return: dictionary with the data for the ids
    '''
    dictionary = {}
    for biological_id in biological_ids:
        
        perturbation_ids = db.getRecords('Perturbation', ['perturbationId'], {'biologicalReplicateId':biological_id[0]})
        
        id_args = {}
        # If metabolites are indicated
        if len(met_list) != 0:
            res = db.getFiles({'metabolitesFile'}, {'biologicalReplicateId':biological_id[0], 'perturbationId': 'null'})
            for i, files in enumerate(res):
                headers = pd.read_csv(files[0], sep=" ").columns
                if set(met_list).issubset(set(headers.tolist())):
                    id_args = {'biologicalReplicateId':biological_id[0], 'perturbationId': 'null'}
        else:
            id_args = {'biologicalReplicateId':biological_id[0], 'perturbationId': 'null'}
        
        if 'biologicalReplicateId' in id_args:
            files_res = db.getFiles(file_types, id_args)
            biol_rep_metadata = db.getRecords('BiologicalReplicate', biol_rep_metadata_fields, {'biologicalReplicateId':biological_id[0]})
            biol_rep_metadata_dict = dict(zip(biol_rep_metadata_fields, biol_rep_metadata[0]))

            dictionary[biological_id[0]] = {'metadata':{}}
            dictionary[biological_id[0]]['metadata'] = biol_rep_metadata_dict

            dictionary[biological_id[0]]['0'] = {'files': ''}
            dictionary[biological_id[0]]['0']['files'] = files_res
        
        # Each perturbations
        for perturbation_id in perturbation_ids:
            
            id_args = {}
            if len(met_list) != 0:
                res = db.getFiles({'metabolitesFile'}, {'biologicalReplicateId':biological_id[0], 'perturbationId': perturbation_id[0]})
                for i, files in enumerate(res):
                    headers = pd.read_csv(files[0], sep=" ").columns
                    if set(met_list).issubset(set(headers.tolist())):
                        id_args = {'biologicalReplicateId':biological_id[0], 'perturbationId': perturbation_id[0]}
            else:
                id_args = {'biologicalReplicateId':biological_id[0], 'perturbationId': perturbation_id[0]}
                
            if 'perturbationId' in id_args:
                files_res = db.getFiles(file_types, id_args)
                pert_metadata = db.getRecords('Perturbation', pert_metadata_fields, {'perturbationId':id_args['perturbationId']})
                pert_metadata_dict = dict(zip(pert_metadata_fields, pert_metadata[0]))

                dictionary[biological_id[0]][perturbation_id[0]] = {'metadata': '', 'files': ''}
                dictionary[biological_id[0]][perturbation_id[0]]['metadata'] = pert_metadata_dict
                dictionary[biological_id[0]][perturbation_id[0]]['files'] = files_res

    return dictionary

def writeResultsTxt(dictionary):
    ''' Write txt and zip from the data dictionary
    
    :param: dictionary
    '''

    zip_file_name = getZipName(LOCAL_DIRECTORY)
    zip_file = ZipFile(LOCAL_DIRECTORY+zip_file_name, mode="w")

    with open(PROJECT_DIRECTORY+'IntermediateFiles/README.txt', 'w') as out_file:
        if len(dictionary) == 0:
            out_file.write('This parameters returned no biological replicate!')
        else:
            for key, val in dictionary.items():
                biological_id = key
                print('\nBIOLOGICAL_REPLICATE ID: ', biological_id)
                
                biol_rep = 'BIOLOGICAL_REPLICATE '+str(biological_id)
                out_file.write('-'*100+'\n'+biol_rep+'\n'+'-'*100+'\n')
                
                for key2, val2 in dictionary[biological_id].items():
                    # BiologicalReplicate metadata
                    if key2 == 'metadata':
                        out_file.write('Metadata:\n')
                        lines = writeMetadataTxt(dictionary[biological_id][key2], 'biological_replicate')
                        out_file.write(lines)
                    # BiologicalReplicate perturbations
                    else:
                        perturbation_id = key2
                        print('\tPERTURBATION ID: ', perturbation_id)
                        
                        pert = 'Perturbation '+key2
                        out_file.write('\n'+pert+'\n'+'-'*100+'\n')

                        for key3, val3 in dictionary[biological_id][perturbation_id].items():
                            # Perturbation metadata (if corresponds)
                            if key3 == 'metadata':
                                out_file.write('Metadata:\n')
                                lines = writeMetadataTxt(dictionary[biological_id][perturbation_id]['metadata'], 'perturbation')
                                out_file.write(lines)
                            
                            # Perturbation files
                            if key3 == 'files':
                                out_file.write('Files:\n')
                                for file in dictionary[biological_id][perturbation_id]['files']:
                                    out_file.write('\t'+file[0]+'\n') #abundance
                                    out_file.write('\t'+file[1]+'\n') #metabolites
                                    out_file.write('\t'+file[2]+'\n') #ph
                                    
                                    regex = PROJECT_DIRECTORY+'(.*)'
                                    zip_file.write(file[0], re.findall(regex, file[0])[0])
                                    zip_file.write(file[1], re.findall(regex, file[1])[0])
                                    zip_file.write(file[2], re.findall(regex, file[2])[0])

    # Save README.txt in ZIP
    zip_file.write(PROJECT_DIRECTORY+'IntermediateFiles/README.txt', 'README.txt')
    zip_file.close()
    print('\nZIP file created: '+zip_file_name+'\n')
        
def writeMetadataTxt(dict, type):
    ''' 
    Writes the metadata part of the dictionary
    
    :param dict: dictionary with the metadata
    :param type: metadata from biological replicate/perturbation
    :return: lines: str 
    '''
    if type == 'biological_replicate':
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
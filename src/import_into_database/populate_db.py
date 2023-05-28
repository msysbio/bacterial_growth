import os
import pandas as pd

from constants import *

from utils import findOccurrences, transformStringIntoList
from import_into_database.yml_functions import read_yml
from import_into_database.bash_functions import clusterHeaders, getFiles
import db_functions as db

def populate_db(args):
    '''
    This function reads the yml file with the information to populate the database and parses it depending on the keys of the values.
    It calls functions to set the biological replicate/perturbation/replicate ids or gets them from the yml file
    It calls db functions to introduce the information in the corresponding db tables

    :param args: user input choice
    '''
    info_file = args.info_file
    info = read_yml(info_file)

    if 'STUDY' in info:
        study = {
            'studyName': info['STUDY'][0]['NAME'],
            'studyDescription': info['STUDY'][0]['DESCRIPTION']
        }
        study_filtered = {k: v for k, v in study.items() if v is not None}
        if len(study_filtered)>0:
            study_id = db.addRecord('Study', study_filtered)
            print('\nSTUDY ID: ', study_id)
        else: 
            print('You must introduce some study information')
            exit()
         
    elif 'STUDY_ID' in info:
        study_id = info['STUDY_ID']
        print('\nSTUDY ID: ', study_id)
    

    if 'BIOLOGICAL_REPLICATE' in info:
        biological_replicates = info['BIOLOGICAL_REPLICATE']    
        for biological_replicate in biological_replicates:
            # ------------------------------------------------------------------------------------
            # REACTOR ==> REACTOR_ID
            reactor = {
                'reactorName': biological_replicate['REACTOR']['NAME']['value'],
                'volume': "{:.2f}".format(biological_replicate['REACTOR']['VOLUME']['value']),
                'atmosphere': "{:.2f}".format(biological_replicate['REACTOR']['ATMOSPHERE']['value']),
                'stirring_speed': "{:.2f}".format(biological_replicate['REACTOR']['STIRRING_SPEED']['value']),
                'reactorMode': biological_replicate['REACTOR']['MODE']['value'],
                'reactorDescription': biological_replicate['REACTOR']['DESCRIPTION']['value'],
            }
            reactor_filtered = {k: v for k, v in reactor.items() if v is not None}
            if len(reactor_filtered)>0: reactor_id = db.addRecord('Reactor',reactor_filtered)
            else: reactor_id=None
            print('\tREACTOR ID: ', reactor_id)
            
            # ------------------------------------------------------------------------------------
            # PRECULTIVATION ==> PRECULTIVATION_ID        
            precultivation_id = None
            print('\tPRECULTIVATION ID: ', precultivation_id)
            
            # ------------------------------------------------------------------------------------
            # MEDIA ==> MEDIA_ID
            if biological_replicate['MEDIA']['MEDIA_PATH']['value']:
                media_file = os.path.abspath(biological_replicate['MEDIA']['MEDIA_PATH']['value'])
                path_end = max(findOccurrences(media_file, "/"))
                media_file_name = media_file[path_end+1:]

                media_analysis_file = PROJECT_DIRECTORY + MEDIA_ANALYSIS_FILE
                media_args = [PROJECT_DIRECTORY, media_file, media_file_name]
                mediaFiles = getFiles(media_analysis_file, media_args, MEDIA_LIST)
                
                for i, f in enumerate(mediaFiles):
                    media = {
                        'mediaName': biological_replicate['MEDIA']['NAME']['value'],
                        'mediaFile': f
                    }
                    media_filtered = {k: v for k, v in media.items() if v is not None}
                    
                    if len(media_filtered)>0: media_id = db.addRecord('Media',media_filtered)
                    else: media_id=None
                    
                    print('\tMEDIA ID: ', media_id)
            
            # ------------------------------------------------------------------------------------
            # ==> BiologicalReplicate table
            biol_rep_positions = transformStringIntoList(biological_replicate['PLATE']['POSITION']['value'], ',')
            biol_rep_dir = transformStringIntoList(biological_replicate['FILES']['value'], ',')

            for i, biol_rep_position in enumerate(biol_rep_positions):
                
                biological_id = setBiologicalReplicateId(study_id)
            
                biol_rep = {
                    'studyId': study_id,
                    'biologicalReplicateId': biological_id,
                    'reactorId': reactor_id,
                    'precultivationId': precultivation_id,
                    'mediaId': media_id,
                    'biologicalReplicateName': biological_replicate['NAME']['value'],
                    'plateId': biological_replicate['PLATE']['ID']['value'],
                    'platePosition': biol_rep_position,
                    'blank': biological_replicate['BLANK']['value'],
                    'inoculumConcentration': "{:.2f}".format(biological_replicate['INOCULUM_CONCENTRATION']['value']),
                    'inoculumVolume': "{:.2f}".format(biological_replicate['INOCULUM_VOLUME']['value']),
                    'initialPh': "{:.2f}".format(biological_replicate['INITIAL_PH']),
                    'initialTemperature': "{:.2f}".format(biological_replicate['INITIAL_TEMPERATURE']['value']),
                    'carbonSource': biological_replicate['CARBON_SOURCE']['value'],
                    'antibiotic': biological_replicate['ANTIBIOTIC']['value'],
                    'biologicalReplicateDescription': biological_replicate['DESCRIPTION']['value']
                }
            
                biological_replicate_filtered = {k: v for k, v in biol_rep.items() if v is not None}
                db.addRecord('BiologicalReplicate', biological_replicate_filtered)
                print('\nBIOLOGICAL_REPLICATE ID: ', biological_id)

                # ------------------------------------------------------------------------------------
                # BACTERIA ==> if BLANK=False
                if biological_replicate['BLANK']['value'] == 0:
                    bacterias = biological_replicate['BACTERIA']
                    for bacteria in bacterias:
                        bact = {
                            'bacteriaGenus': bacteria['GENUS'],
                            'bacteriaSpecies': bacteria['SPECIES'],
                            'bacteriaStrain': bacteria['STRAIN']
                        }
                        bacteria_filtered = {k: v for k, v in bact.items() if v is not None}

                        if len(bacteria_filtered)>0: 
                            bacteria_id = db.addRecord('Bacteria',bacteria_filtered)
                            community = {
                                'bacteriaId': bacteria_id,
                                'biologicalReplicateId': biological_id
                            }
                            community_filtered = {k: v for k, v in community.items() if v is not None}
                            db.addRecord('BacteriaCommunity',community_filtered)                   

                ### Files analysis
                print(biol_rep_dir[i])
                if biol_rep_dir[i]:
                    files_dir = os.path.abspath(biol_rep_dir[i]) + '/'

                    biol_rep_analysis_file = PROJECT_DIRECTORY + BIOLOGICAL_REPLICATE_ANALYSIS_FILE
                    biol_rep_args = [PROJECT_DIRECTORY, files_dir, biological_id]
                    biol_rep_files = getFiles(biol_rep_analysis_file, biol_rep_args, BIOLOGICAL_REPLICATES_LIST)

                    headers_dict = clusterHeaders(PROJECT_DIRECTORY + HEADERS_FILE)
                    
                    addReplicates(headers_dict, biol_rep_files, biological_id=biological_id, perturbation_id=None)
            
    elif 'BIOLOGICAL_ID' in info:
        biological_id = info['BIOLOGICAL_ID']
        print('\nBIOLOGICAL_REPLICATE ID: ', biological_id)
    
    
    if 'PERTURBATION' in info:
        perturbations = info['PERTURBATION']
        for perturbation in perturbations:

            pert_positions = transformStringIntoList(perturbation['PLATE']['POSITION']['value'], ',')
            pert_dir = transformStringIntoList(perturbation['FILES']['value'], ',')

            for i, pert_position in enumerate(pert_positions):
                
                perturbation_id = setPerturbationId(biological_id)
                pert = {
                    'perturbationId': perturbation_id,
                    'biologicalReplicateId': biological_id,
                    'plateId': perturbation['PLATE']['ID']['value'],
                    'platePosition': pert_position,
                    'property': perturbation['PROPERTY']['value'],
                    'newValue': perturbation['NEW_VALUE']['value'],
                    'startTime': perturbation['STARTING_TIME']['value'],
                    'endTime': perturbation['ENDING_TIME']['value'],
                    'perturbationDescription': perturbation['DESCRIPTION']['value']
                }
                perturbation_filtered = {k: v for k, v in pert.items() if v is not None}
                db.addRecord('Perturbation', perturbation_filtered)
                print('\nPERTURBATION ID: ', perturbation_id)

                ### Files analysis
                print(pert_dir[i])
                if pert_dir[i]:
                    files_dir = os.path.abspath(pert_dir[i]) + '/'
                    
                    biol_rep_analysis_file = PROJECT_DIRECTORY + BIOLOGICAL_REPLICATE_ANALYSIS_FILE
                    biol_rep_args = [PROJECT_DIRECTORY, files_dir, biological_id, perturbation_id]
                    biol_rep_files = getFiles(biol_rep_analysis_file, biol_rep_args, BIOLOGICAL_REPLICATES_LIST) #this will generate the new HEADERS_FILE

                    headers_dict = clusterHeaders(PROJECT_DIRECTORY + HEADERS_FILE)

                    addReplicates(headers_dict, biol_rep_files, biological_id=biological_id, perturbation_id=perturbation_id)
                        
    elif 'PERTURBATION_ID' in info:
        perturbation_id = info['PERTURBATION_ID']
        print('\nPERTURBATION ID: ', perturbation_id)
     
    
    if 'FILES' in info:
        files_dir = os.path.abspath(info['FILES']) + '/'

        biol_rep_analysis_file = PROJECT_DIRECTORY + BIOLOGICAL_REPLICATE_ANALYSIS_FILE
        biol_rep_args = [PROJECT_DIRECTORY, files_dir]
        biol_rep_files = getFiles(biol_rep_analysis_file, biol_rep_args, BIOLOGICAL_REPLICATES_LIST) #this will generate the new HEADERS_FILE

        headers_dict = clusterHeaders(PROJECT_DIRECTORY + HEADERS_FILE)
        
        addReplicates(headers_dict, biol_rep_files, biological_id=biological_id, perturbation_id=perturbation_id)

def setBiologicalReplicateId(study_id):
    '''
    This function sets up the biological replicate id depending on the study id
    
    :parama study_id in which the biological replicate is added
    :return biological_id
    '''
    number_biol_rep = db.countRecords('BiologicalReplicate', {'studyId': str(study_id)})
    biological_id = str(int(study_id)*100 + number_biol_rep + 1)
    return biological_id

def setPerturbationId(biological_id):
    '''
    This function sets up the perturbation id depending on the biological replicate id
    
    :parama biological_id in which the perturbation is added
    :return perturbation_id
    '''
    number_pert = db.countRecords('Perturbation', {'biologicalReplicateId': str(biological_id)})
    perturbation_id = biological_id + '.' + str(number_pert + 1)
    return perturbation_id

def addReplicates(headers, files, biological_id, perturbation_id):
    '''
    This function saves each file as a technical replicate
    For this, it calculates the replicate id with the biological_id providad (and the perturbation_id)
    Separates the file data into abundances/ph/metabolites
    Saves in txt file and in the db table

    :param headers: dict with categories as keys to separate df into sub_dfs
    :param files
    :param biological_id where replicates are added
    :param perturbation_id where replicates are added
    '''
    if perturbation_id == None:
        id = biological_id
        number_rep = db.countRecords('TechnicalReplicate', {'biologicalReplicateId': str(id)})
    else:
        id = perturbation_id
        number_rep = db.countRecords('TechnicalReplicate', {'perturbationId': str(id)})

    print('\n- The ID in which the replicate files will be added is: ',id)
    print('- The number of replicates already in that id: ',number_rep)
    for i, f in enumerate(files):
        technical_id = str(id) + '_' + str(number_rep + i + 1)
        
        #Get directory of the provided paths
        path_end = max(findOccurrences(f, "/"))
        path = f[:path_end+1]

        #Read file with all the data
        df = pd.read_table(f, sep=" ")
        
        growth_data = df[df.columns.intersection(headers['abundance'])]
        growth_data = growth_data.round({'OD': 3})
        
        ph_data = df[df.columns.intersection(headers['ph'])]
        ph_data = ph_data.round({'pH': 3})

        metabolites_data = df[df.columns.intersection(headers['metabolites'])]

        # If len(df.columns) <= 1 (only time column), we do not save it
        if len(growth_data.columns) > 1:
            g_path = path+'abundance_file.txt'
            growth_data.to_csv(g_path, sep=" ", index=False)
        else: g_path = None
        
        if len(ph_data.columns) > 1:    
            p_path = path+'pH_file.txt'
            ph_data.to_csv(p_path, sep=" ", index=False)
        else: p_path = None

        if len(metabolites_data.columns) > 1:
            m_path = path+'metabolites_file.txt'
            metabolites_data.to_csv(m_path, sep=" ", index=False)
        else: m_path = None

        rep = {
            'technicalReplicateId': technical_id,
            'biologicalReplicateId': biological_id,
            'perturbationId': perturbation_id,
            'abundanceFile': g_path,
            'metabolitesFile': m_path,
            'phFile': p_path
            }
        
        replicate_filtered = {k: v for k, v in rep.items() if v is not None}
        db.addRecord('TechnicalReplicate', replicate_filtered)
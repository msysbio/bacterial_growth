import os
import pandas as pd
from constants import *

from utils import findOccurrences
from yml_functions import read_yml
from bash_functions import clusterHeaders, getFiles
import db_functions as db

def populate_db(args):

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
    

    if 'EXPERIMENT' in info:
        experiments = info['EXPERIMENT']    
        for experiment in experiments:
            experiment_id = setExperimentId(study_id)
            # ------------------------------------------------------------------------------------
            # REACTOR ==> REACTOR_ID
            reactor = {
                'reactorName': experiment['REACTOR']['NAME']['value'],
                'volume': experiment['REACTOR']['VOLUME']['value'],
                'atmosphere': experiment['REACTOR']['ATMOSPHERE']['value'],
                'stirring_speed': experiment['REACTOR']['STIRRING_SPEED']['value'],
                'reactorMode': experiment['REACTOR']['MODE']['value'],
                'reactorDescription': experiment['REACTOR']['DESCRIPTION']['value'],
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
            if experiment['MEDIA']['MEDIA_PATH']['value']:
                media_file = os.path.abspath(experiment['MEDIA']['MEDIA_PATH']['value'])
                path_end = max(findOccurrences(media_file, "/"))
                media_file_name = media_file[path_end+1:]

                media_analysis_file = PROJECT_DIRECTORY + MEDIA_ANALYSIS_FILE ##SERVER_DIRECTORY
                media_args = [PROJECT_DIRECTORY, media_file, media_file_name] ##LOCAL_DIRECTORY
                mediaFiles = getFiles(media_analysis_file, media_args, MEDIA_LIST)
                
                for i, f in enumerate(mediaFiles):
                    media = {
                        'mediaName': experiment['MEDIA']['NAME']['value'],
                        'mediaFile': f
                    }
                    media_filtered = {k: v for k, v in media.items() if v is not None}
                    
                    if len(media_filtered)>0: media_id = db.addRecord('Media',media_filtered)
                    else: media_id=None
                    
                    print('\tMEDIA ID: ', media_id)

            # ------------------------------------------------------------------------------------
            exp = {
                'studyId': study_id,
                'experimentId': experiment_id,
                'reactorId': reactor_id,
                'precultivationId': precultivation_id,
                'mediaId': media_id,
                'experimentName': experiment['NAME']['value'],
                'plateId': experiment['PLATE']['ID']['value'],
                'plateColumn': experiment['PLATE']['COLUMN']['value'],
                'plateRow': experiment['PLATE']['ROW']['value'],
                'blank': experiment['BLANK']['value'],
                'inoculumConcentration': experiment['INOCULUM_CONCENTRATION']['value'],
                'inoculumVolume': experiment['INOCULUM_VOLUME']['value'],
                'initialPh': experiment['INITIAL_PH'],
                'initialTemperature': experiment['INITIAL_TEMPERATURE']['value'],
                'carbonSource': experiment['CARBON_SOURCE']['value'],
                'antibiotic': experiment['ANTIBIOTIC']['value'],
                'experimentDescription': experiment['DESCRIPTION']['value']   
            }
            experiment_filtered = {k: v for k, v in exp.items() if v is not None}
            db.addRecord('Experiment', experiment_filtered)
            print('EXPERIMENT ID: ', experiment_id)

            # ------------------------------------------------------------------------------------
            # BACTERIA ==> if BLANK=False
            if experiment['BLANK']['value'] == 0:
                bacterias = experiment['BACTERIA']
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
                            'experimentId': experiment_id
                        }
                        community_filtered = {k: v for k, v in community.items() if v is not None}
                        db.addRecord('BacteriaCommunity',community_filtered)                   
            
            ### Files analysis
            if experiment['FILES']['value']:
                files_dir = os.path.abspath(experiment['FILES']['value']) + '/'

                exp_analysis_file = PROJECT_DIRECTORY + EXPERIMENT_ANALYSIS_FILE ##SERVER_DIRECTORY
                exp_args = [PROJECT_DIRECTORY, files_dir, experiment_id] ##LOCAL_DIRECTORY
                exp_files = getFiles(exp_analysis_file, exp_args, EXPERIMENTS_LIST) #this will generate the new HEADERS_FILE

                headers_dict = clusterHeaders(PROJECT_DIRECTORY + HEADERS_FILE) ##SERVER_DIRECTORY
                
                addReplicates(headers_dict, exp_files, experiment_id=experiment_id, perturbation_id=None)
            
    elif 'EXPERIMENT_ID' in info:
        experiment_id = info['EXPERIMENT_ID']
        print('\nEXPERIMENT ID: ', experiment_id)
    
    
    if 'PERTURBATION' in info:
        perturbations = info['PERTURBATION']
        for perturbation in perturbations:

            perturbation_id = setPerturbationId(experiment_id)
            pert = {
                'perturbationId': perturbation_id,
                'experimentId': experiment_id,
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
            if perturbation['FILES']['value']:
                files_dir = os.path.abspath(perturbation['FILES']['value']) + '/'
                
                exp_analysis_file = PROJECT_DIRECTORY + EXPERIMENT_ANALYSIS_FILE
                exp_args = [PROJECT_DIRECTORY, files_dir, experiment_id, perturbation_id]
                exp_files = getFiles(exp_analysis_file, exp_args, EXPERIMENTS_LIST) #this will generate the new HEADERS_FILE

                headers_dict = clusterHeaders(PROJECT_DIRECTORY + HEADERS_FILE)

                addReplicates(headers_dict, exp_files, experiment_id=experiment_id, perturbation_id=perturbation_id)
                        
    elif 'PERTURBATION_ID' in info:
        perturbation_id = info['PERTURBATION_ID']
        print('\nPERTURBATION ID: ', perturbation_id)
     
    
    if 'FILES' in info:
        files_dir = os.path.abspath(info['FILES']) + '/'

        exp_analysis_file = PROJECT_DIRECTORY + EXPERIMENT_ANALYSIS_FILE
        exp_args = [PROJECT_DIRECTORY, files_dir]
        exp_files = getFiles(exp_analysis_file, exp_args, EXPERIMENTS_LIST) #this will generate the new HEADERS_FILE

        headers_dict = clusterHeaders(PROJECT_DIRECTORY + HEADERS_FILE)
        
        addReplicates(headers_dict, exp_files, experiment_id=experiment_id, perturbation_id=perturbation_id)

def setExperimentId(study_id):
    number_exp = db.countRecords('Experiment', 'studyId', str(study_id))
    experiment_id = str(int(study_id)*100 + number_exp + 1)
    return experiment_id

def setPerturbationId(experiment_id):
    number_pert = db.countRecords('Perturbation', 'experimentId', str(experiment_id))
    perturbation_id = experiment_id + '.' + str(number_pert + 1)
    return perturbation_id

def addReplicates(headers, files, experiment_id, perturbation_id):

    if perturbation_id == None:
        id = experiment_id
        number_rep = db.countRecords('TechnicalReplicate', 'experimentId', str(id))
    else:
        id = perturbation_id
        number_rep = db.countRecords('TechnicalReplicate', 'perturbationId', str(id))

    print('\n- The ID in which the replicate files will be added is: ',id)
    print('- The number of replicates already in that id: ',number_rep)
    for i, f in enumerate(files):
        replicate_id = str(id) + '_' + str(number_rep + i + 1)
        # print('\n\tREPLICATE ID: ', replicate_id)
        
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
            'replicateId': replicate_id,
            'experimentId': experiment_id,
            'perturbationId': perturbation_id,
            'abundanceFile': g_path,
            'metabolitesFile': m_path,
            'phFile': p_path
            }
        
        replicate_filtered = {k: v for k, v in rep.items() if v is not None}
        db.addRecord('TechnicalReplicate', replicate_filtered)
            
    print('- Last replicate id: ',replicate_id)
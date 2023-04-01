import os
import re
import pandas as pd
from utils import (
    runBash, 
    getMatchingList
)
from utils import findOccurrences
from yml_functions import (read_yml)
import db_functions as db

# ===========================================================================================
# Variables:
# ===========================================================================================

PROJECT_DIRECTORY = '/Users/julia/bacterialGrowth_thesis/'
LAB_ANALYSIS_FILE = 'src/Lab_files_analysis2.sh'

HEADERS_FILE = 'IntermediateFiles/lab_headers.txt'
EXPERIMENTS_LIST = 'IntermediateFiles/listOfFiles.list'

# ===========================================================================================
# ===========================================================================================

def populate_db(args):

    info_file = args.info_file
    info = read_yml(info_file)

    if 'STUDY' in info:
        study = info['STUDY']
        study_id = db.addRecord('Study', study)
        print('\nSTUDY ID: ', study_id)
    
    elif 'STUDY_ID' in info:
        study_id = info['STUDY_ID']
        print('\nSTUDY ID: ', study_id)
    

    if 'EXPERIMENT' in info:
        experiments = info['EXPERIMENT']    
        for experiment in experiments:
            # ------------------------------------------------------------------------------------
            # REACTOR ==> REACTOR_ID
            reactor = {
                'reactorName': experiment['REACTOR']['NAME']['value'],
                'volume': experiment['REACTOR']['VOLUME']['value']
            }
            reactor_filtered = {k: v for k, v in reactor.items() if v is not None}
            # reactor_id = db.addReactor(reactor_filtered)
            reactor_id = db.addRecord('Reactor',reactor_filtered)
            print('\tREACTOR ID: ', reactor_id)
            
            # ------------------------------------------------------------------------------------
            # PRECULTIVATION ==> PRECULTIVATION_ID        
            precultivation_id = 1
            print('\tPRECULTIVATION ID: ', precultivation_id)
            
            # ------------------------------------------------------------------------------------
            # MEDIA ==> MEDIA_ID
            media = {
                'mediaName': experiment['MEDIA']['NAME']['value'],
                'mediaFile': experiment['MEDIA']['MEDIA_PATH']['value']
            }
            media_filtered = {k: v for k, v in media.items() if v is not None}
            media_id = db.addRecord('Media',media_filtered)
            print('\tMEDIA ID: ', media_id)

            # ------------------------------------------------------------------------------------
            experiment_id = setExperimentId(study_id)
            exp = {
                'studyId': study_id,
                'experimentId': experiment_id,
                'reactorId': reactor_id,
                'precultivationId': precultivation_id,
                'mediaId': media_id,
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
            
            ### Files analysis 
            files_dir = os.path.abspath(experiment['FILES']['value']) + '/'
            files = analyzeLabDir(files_dir)
            headers_dict = clusterHeaders(PROJECT_DIRECTORY + HEADERS_FILE)

            addReplicates(headers_dict, files, experiment_id=experiment_id, perturbation_id=None)
            print('\nEXPERIMENT ID: ', experiment_id)

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
            # db.addPerturbation(perturbation_id, experiment_id, perturbation_filtered)
            
            ### Files analysis 
            files_dir = os.path.abspath(perturbation['FILES']['value']) + '/'
            print('-->', files_dir)
            files = analyzeLabDir(files_dir)
            headers_dict = clusterHeaders(PROJECT_DIRECTORY + HEADERS_FILE)

            addReplicates(headers_dict, files, experiment_id=experiment_id, perturbation_id=perturbation_id)
            print('\nPERTURBATION ID: ', perturbation_id)
    
    elif 'PERTURBATION_ID' in info:
        perturbation_id = info['PERTURBATION_ID']
        print('\nPERTURBATION ID: ', perturbation_id)
    
    

def analyzeLabDir(dir):
    labAnalysisFile = PROJECT_DIRECTORY + LAB_ANALYSIS_FILE

    # Analyse the provided files and get the necessary information from them
    runBash(labAnalysisFile, [PROJECT_DIRECTORY, dir])

    # experimentName = [x.split(' ')[1] for x in open(PROJECT_DIRECTORY + 'IntermediateFiles/experiments_info.txt').readlines()][1]
    experimentFiles = open(PROJECT_DIRECTORY + EXPERIMENTS_LIST, "r").readlines()
    experimentFiles = list(map(lambda s: s.strip(), experimentFiles))
    
    return experimentFiles

def clusterHeaders(file):
    """ This function separates the received list of headers into categories: abundance, metaboites, ph"""

    with open(file) as f:
        lst = f.read().splitlines()

    abundance_regex = re.compile(r'.*time.* | .*liquid.* | .*active.* | .*OD.*', flags=re.I | re.X)
    # abundance_regex = re.compile(r'time | liquid | active | OD', flags=re.I | re.X)
    ph_regex = re.compile(r'.*time.* | .*ph.*', flags=re.I | re.X)

    abundance_headers = getMatchingList(abundance_regex, lst)
    ph_headers = getMatchingList(ph_regex, lst)

    not_metabolites_list = list(set(abundance_headers) | set(ph_headers))
    metabolites_headers = set(lst) - set(not_metabolites_list)
    metabolites_headers = list(metabolites_headers)
    metabolites_headers.append('time')

    headers = {'abundance': abundance_headers,'metabolites': metabolites_headers,'ph': ph_headers}

    return headers    

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

    print('\nThe ID in which the replicate files will be added is: ',id)
    print('The number of replicates already in that id: ',number_rep)
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

        # print(i, replicate_id)
        # print(g_path,'\n',m_path,'\n',p_path,'\n\n')

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
            
        # db.addReplicate(str(replicate_id), str(experiment_id), str(perturbation_id))
    print('\nLast replicate id: ',replicate_id)
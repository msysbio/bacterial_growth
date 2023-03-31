import os
import re
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
LAB_ANALYSIS_FILE = 'Scripts/Lab_files_analysis2.sh'

HEADERS_FILE = 'IntermediateFiles/lab_headers.txt'
EXPERIMENTS_LIST = 'IntermediateFiles/listOfFiles.list'

# Will come form the parser
EXP_DESCRIPTION = 'This experiment was done in Brussels.'
CULT_DESCRIPTION = 'In this perturbation, we kept pH at 5'
REP_DESCRIPTION = 'Replicate number #'

# ===========================================================================================
# ===========================================================================================

def populate_db(args):

    info_file = args.info_file
    info = read_yml(info_file)

    if 'STUDY' in info:
        study = 0
        study_id = db.addStudy(study)
    else:
        study_id = info['STUDY_ID']
    
    if 'EXPERIMENT' in info:
        experiment = 0
        experiment_id = getExperimentId(study_id)
        db.addExperiment(experiment_id, study_id, experiment)
        # db.addReplicates
    else:
        exp_id = info['EXPERIMENT_ID']

    if 'PERTURBATION' in info:
        perturbation = 0
        perturbation_id = getPerturbationId(experiment_id)
        db.addPerturbation(perturbation_id, experiment_id, perturbation)
        # db.addReplicates
    else:
        perturbation_id = info['PERTURBATION_ID']

    if 'FILES' in info:
        files = 0 #This does nothing -> remove when I have something inside this if conditon
        # db.addReplicates

    

def analyzeLabDir(dir):
    labAnalysisFile = PROJECT_DIRECTORY + LAB_ANALYSIS_FILE

    # Analyse the provided files and get the necessary information from them
    runBash(labAnalysisFile, [PROJECT_DIRECTORY, dir])
    # headers_dict = clusterHeaders(PROJECT_DIRECTORY + HEADERS_FILE)

    experimentName = [x.split(' ')[1] for x in open(PROJECT_DIRECTORY + 'IntermediateFiles/experiments_info.txt').readlines()][1]
    experimentFiles = open(PROJECT_DIRECTORY + EXPERIMENTS_LIST, "r").readlines()
    experimentFiles = list(map(lambda s: s.strip(), experimentFiles))

    return [experimentName, experimentFiles]


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

def getExperimentId(study_id):
    number_exp = db.countRecords('Experiment', 'studyId', str(study_id))
    experiment_id = study_id*100 + number_exp + 1
    return experiment_id

def getPerturbationId(experiment_id):
    number_pert = db.countRecords('Perturbation', 'experimentId', str(experiment_id))
    perturbation_id = str(experiment_id) + '.' + str(number_pert + 1)
    return perturbation_id

def addReplicates(cultId, headers, files):
    number_rep = db.countRecords('TechnicalReplicates', 'cultivationId', str(cultId))

    for i, f in enumerate(files):
        repId = str(cultId) + '_' + str(number_rep + i + 1)
        db.addReplicate(str(repId), str(cultId))
        
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
            db.addReplicateFile(repId,bacterialAbundanceFile=g_path)
        
        if len(ph_data.columns) > 1:    
            p_path = path+'pH_file.txt'
            ph_data.to_csv(p_path, sep=" ", index=False)
            db.addReplicateFile(repId,phFile=p_path)
        
        if len(metabolites_data.columns) > 1:
            m_path = path+'metabolites_file.txt'
            metabolites_data.to_csv(m_path, sep=" ", index=False)
            db.addReplicateFile(repId,metabolitesFile=m_path)

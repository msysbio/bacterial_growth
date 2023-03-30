import os
import re

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from parser import bacterial_parser
from utils import (
    runBash, 
    getMatchingList
)
from populate import (
    addExperiment,
    addCultivation,
    addReplicates
)
from read_yml import (
    getExperimentInfo, 
    getCultivationInfo
)
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

def main():

    args = bacterial_parser()

    experimentDir = os.path.abspath(args.exp_files) + '/'
    experiment = analyzeLabDir(experimentDir)
    experimentName = experiment[0]
    experimentFiles = experiment[1]

    headers_dict = clusterHeaders(PROJECT_DIRECTORY + HEADERS_FILE)

    infoFile = args.info
    
    if args.option == 1:
        print('\n\n--> Create a new experiment, with its corresponding cultivation conditions and several replicates.')
        newExperiment = getExperimentInfo(infoFile)
        newCultivation = getCultivationInfo(infoFile)

        if 'experimentName' not in newExperiment:
            newExperiment['experimentName'] = experimentName

        expId = addExperiment(newExperiment)
        cultId = addCultivation(expId, newCultivation)
        addReplicates(cultId, headers_dict, experimentFiles)

    elif args.option == 2:
        print('\n\n--> Add new cultivation conditions to an exisiting experiment with the corresponding replicates. An experiment ID must be provided.')

        # expId = 
        cultId = addCultivation(expId)
        addReplicates(cultId, headers_dict, experimentFiles)


    elif args.option == 3:
        print('\n\n--> Add more replicates to certain cultivation conditions. A cultivation ID must be provided.')

        # cultId = 
        addReplicates(cultId, headers_dict, experimentFiles)

    else:
        print(0)



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


if __name__ == "__main__":
    main()
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
    read_yaml,
    write_yaml,
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
    infoFile = args.info

    if args.option == 1:
        print('\n\n--> Create a new experiment, with corresponding experiments.')
        
        # populate.yml


    elif args.option == 2:
        print('\n\n--> Add a new experiment to an existing study.')

        # populate_2.yml
        
        info = read_yaml(infoFile)
        print(info)
        write_yaml(info)


    elif args.option == 3:
        print('\n\n--> Add a new perturbation to an existing study.')

        # populate_3.yml


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
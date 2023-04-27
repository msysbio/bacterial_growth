import os
from constants import *
from utils import getMatchingList

def runBash(file, arguments=[]):
    '''
    :param file: .sh file to run
    :param arguments: list with all the arguments for the bash order
    '''
    bash_script_params = ['sh', file]
    
    if type(arguments) == list:
        for arg in arguments:
            bash_script_params.append(arg)
    elif type(arguments) == str:
        bash_script_params.append(arguments)
    
    bash_script_command = " ".join(bash_script_params)
            
    if os.system(bash_script_command) != 0:
        print("! The bash script failed to run.")
        print("! Exit")
        exit()

def getFiles(bash_file, bash_args, list_files):
    '''
    :param bash_file: .sh to run to get the wanted files
    :param bash_args: list with all the arguments for the bash order
    :param list_files: name of the file created by the .sh file with a list of files
    :return list of files
    '''
    # Analyse the provided files and get the necessary information from them
    runBash(bash_file, bash_args)

    files = open(PROJECT_DIRECTORY + list_files, "r").readlines()
    files = list(map(lambda s: s.strip(), files))
    
    return files

def clusterHeaders(file):
    """ 
    Read the file headers and cluster them into known categories

    :param file
    :return headers: dictionary with categories as keys
    """

    with open(file) as f:
        lst = f.read().splitlines()

    abundance_headers = getMatchingList(abundance_regex, lst)
    ph_headers = getMatchingList(ph_regex, lst)

    not_metabolites_list = list(set(abundance_headers) | set(ph_headers))
    metabolites_headers = set(lst) - set(not_metabolites_list)
    metabolites_headers = list(metabolites_headers)
    metabolites_headers.append('time')

    headers = {'abundance': abundance_headers,'metabolites': metabolites_headers,'ph': ph_headers}

    return headers    

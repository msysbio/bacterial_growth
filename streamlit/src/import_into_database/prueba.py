import os
import db_functions as db

media_file = os.path.abspath('/Users/sofia/Desktop/thesis/bacterial_growth/src/mediafile.txt')
print(media_file)

def findOccurrences(string, ch):
    '''
    This function returns a list with all the positions of the string that contain the character ch

    :param string
    :param ch: character to look for
    :return list with positions
    '''
    return [i for i, letter in enumerate(string) if letter == ch]

ocurence = findOccurrences(media_file, "\\")
print(ocurence)
path_end = max(findOccurrences(media_file, "\\"))
media_file_name = media_file[path_end+1:]
print(media_file_name)

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

PROJECT_DIRECTORY = 'C:/Users/sofia/Desktop/thesis/bacterial_growth/'

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

MEDIA_LIST = 'IntermediateFiles/listOfMedia.list'
MEDIA_ANALYSIS_FILE = 'src/bash_scripts/media_file_analysis.sh'
media_analysis_file = PROJECT_DIRECTORY + MEDIA_ANALYSIS_FILE
media_args = [PROJECT_DIRECTORY, media_file, media_file_name]
mediaFiles = getFiles(media_analysis_file, media_args, MEDIA_LIST)

print(mediaFiles)


for i, f in enumerate(mediaFiles):
    media = {
        'mediaName': 'media1',
        'mediaFile': f
        }
    media_filtered = {k: v for k, v in media.items() if v is not None}
    print(media_filtered)
    if len(media_filtered)>0: media_id = db.addRecord('Media',media_filtered)
    else: media_id=None
    print('\tMEDIA ID: ', media_id)

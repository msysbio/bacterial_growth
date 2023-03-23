import argparse
from utils import (
    isDir,
    isFile
)

def bacterial_parser():
    parser = argparse.ArgumentParser(description='details',
                                     usage='use "%(prog)s --help" for more information',
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("--option", 
                        type=int,
                        required=True, 
                        choices=[1, 2, 3, 4],
                        help=''' 
    Choose the program's functionality:
        (1): Create a new experiment, with its corresponding cultivation conditions and several replicates.
        (2): Add new cultivation conditions to an exisiting experiment with the corresponding replicates. An experiment ID must be provided.
        (3): Add more replicates to certain cultivation conditions. A cultivation ID must be provided.
        (4): Get information and plots about certain experiments.
    ''')

    parser.add_argument('--info', 
                        type=isFile,
                        help='File with the info of the experiment that is going to be included in the DB or the experiment that is going to be accessed to')

    parser.add_argument('--media-file', 
                        type=isFile,
                        help='File with the media composition used in the experiment')
    
    parser.add_argument('--exp-files', 
                        type=isDir,
                        help='Directory with replicates files')
    


    args = parser.parse_args()

    return args
import argparse
from utils import checkPath

def bacterial_parser():
    parser = argparse.ArgumentParser(description='details',
                                     usage='use "%(prog)s --help" for more information',
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('--dir', 
                        type=checkPath, 
                        help='Directory with replicates files')
    parser.add_argument("--option", 
                        type=int,
                        required=True, 
                        choices=[1, 2, 3],
                        help=''' 
    Choose the program's functionality:
        (1): Create a new experiment, with its corresponding cultivation conditions and several replicates.
        (2): Add new cultivation conditions to an exisiting experiment with the corresponding replicates. An experiment ID must be provided.
        (3): Add more replicates to certain cultivation conditions. A cultivation ID must be provided.
    ''')


    args = parser.parse_args()

    return args
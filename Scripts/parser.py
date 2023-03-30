import argparse
from utils import (
    isDir,
    isFile
)

def bacterial_parser():
    parser = argparse.ArgumentParser(
        description='Create the yml file for th euser to fill in with the information',
        usage='use "%(prog)s --help" for more information',
        formatter_class=argparse.RawTextHelpFormatter)

    # parser.add_argument("--option", 
    #                     type=int,
    #                     required=True, 
    #                     choices=[1, 2, 3],
    #                     help=''' 
    # Choose the program's functionality:
    #     (1): Create a new experiment, with corresponding experiments.
    #     (2): Add a new experiment to an existing study.
    #     (3): Add a new perturbation to an existing study.
    # ''')

    # parser.add_argument('--info', 
    #                     type=isFile,
    #                     help='File with the info of the experiment that is going to be included in the DB or the experiment that is going to be accessed to')

    # parser.add_argument('--media-file', 
    #                     type=isFile,
    #                     help='File with the media composition used in the experiment')
    
    # parser.add_argument('--exp-files', 
    #                     type=isDir,
    #                     help='Directory with replicates files')


    parser.add_argument(
        '-s', '--num_studies', dest='num_studies', help="Number of new studies to introduce in the DB", required=False, type=int
    )
    
    parser.add_argument(
        '-e', '--num_experiments', dest='num_experiments', help="Number of new experiments to introduce in the DB", required=False, type=int
    )

    parser.add_argument(
        '-p', '--num_perturbations', dest='num_perturbations', help="Number of new perturbations to introduce in the DB", required=False, type=int
    )

    parser.add_argument(
        '-f', '--files_dir', dest='files_dir', help="Directory containing the files to introduce in the DB", required=False, type=isDir
    )

    args = parser.parse_args()

    return args
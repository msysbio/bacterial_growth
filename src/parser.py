import argparse
from utils import (
    isDir,
    isFile
)

def bacterial_parser():
    

    parser = argparse.ArgumentParser(
        description='Create the yml file for the user to fill in with the information',
        usage='use "%(prog)s --help" for more information',
        formatter_class=argparse.RawTextHelpFormatter)
    subparsers = parser.add_subparsers(dest='option')
    
    # create the parser for the "createInfoFile" command
    subparser1 = subparsers.add_parser('createInfoFile', help='Parameters needed for creating the YML file with the information that will be put in the DB')
    subparser1.add_argument(
        '-s', '--num_studies', dest='num_studies', help="Number of new studies to introduce in the DB", required=False, type=int
    )
    
    subparser1.add_argument(
        '-e', '--num_experiments', dest='num_experiments', help="Number of new experiments to introduce in the DB", required=False, type=int
    )

    subparser1.add_argument(
        '-p', '--num_perturbations', dest='num_perturbations', help="Number of new perturbations to introduce in the DB", required=False, type=int
    )

    subparser1.add_argument(
        '-f', '--files_dir', dest='files_dir', help="Directory containing the files to introduce in the DB", required=False, type=isDir
    )
    
    
    # create the parser for the "populateDB" command
    subparser2 = subparsers.add_parser('populateDB', help='Pass the YML file with the information that will be put in the DB')
    subparser2.add_argument(
        '-i', '--info_file', dest='info_file', help="Directory with the YML with the experiment information for the DB", required=False, type=isDir
    )

    
    args = parser.parse_args()

    return args


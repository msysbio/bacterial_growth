from bacterial_parser import bacterial_parser

from create_populate_file import create_yml_file
from populate_db import populate_db
from plot import plot
from create_results_file import getInformationFile

from user_inputs import choosePlotOption

def main():

    args = bacterial_parser()
    
    if args.option == 'createInfoFile':
        create_yml_file(args)
    elif args.option == 'populateDB':
        populate_db(args)
    elif args.option == 'plot':
        option = choosePlotOption()
        plot(option)
    elif args.option == 'getResultsFile':
        getInformationFile(args)


if __name__ == "__main__":
    main()


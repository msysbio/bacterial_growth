from bacterial_parser import bacterial_parser

from import_into_database.create_populate_file import create_yml_file
from import_into_database.populate_db import populate_db
from export_from_database.plot import plot
from export_from_database.create_results_file import getInformationFile

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
        if args.bacteria == None and args.metabolites == None:
            print('\n\tERROR: You did not select any parameter. Write --help to see the options.\n')
            exit()
        getInformationFile(args)


if __name__ == "__main__":
    main()


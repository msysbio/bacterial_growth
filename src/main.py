from bacterial_parser import bacterial_parser
from prepare_populate import prepare_populate
from populate_db import populate_db

def main():

    args = bacterial_parser()
    
    if args.option == 'createInfoFile':
        prepare_populate(args)
    elif args.option == 'populateDB':
        populate_db(args)



if __name__ == "__main__":
    main()


# Aim:
#   Add chebi ids and their names in the metabolitename table
# Usage:
#   python populate_metadb.py
# Notes:
#   Make sure you have the secrets.toml file

import pandas as pd
import tomllib  #  Parses TOML files
from pathlib import Path
from sqlalchemy import create_engine, VARCHAR
import argparse

# Create the argument parser
parser = argparse.ArgumentParser(description="Upload metabolites using ChEBI ids, and their synonyms to the database.",
                                 formatter_class=argparse.RawTextHelpFormatter)

# Add the `--mode` argument with predefined choices
mode_message = """Set the mode of your choice:
scratch: will drop all previous metabolites data and load new data
extras: will keep the existing data as is, and add only new data; in case of duplicates, the initial data will be kept
replace: will keep the existing and add new data; in case of duplicates, the new version will replace the initial one
    """
parser.add_argument(
    "--mode",
    choices=["scratch", "extras", "replace"],
    required=True,  # Make this argument mandatory
    help=mode_message
)

# Parse the command-line arguments
args = parser.parse_args()

# Function to get the SQLAlchemy engine
def get_engine():
    """
    Fire a create_engine connection to the MySQL database.
    This function is not to be used in the app. It is only for the purpose of loading
    the metaboltes metadata into the database.
    """
    secrets_file = "../../../config/database.toml"
    secrets = tomllib.loads(Path(secrets_file).read_text())
    secrets_dict = secrets['development']
    user = secrets_dict["username"]
    password = secrets_dict["password"]
    host = secrets_dict["host"]
    port = secrets_dict["port"]
    database = secrets_dict["database"]
    return create_engine(
        url="mysql+pymysql://{0}:{1}@{2}:{3}/{4}".format(
            user, password, host, port, database
        )
    )


# Load the metabolites
excel_file_path = 'metabolites.csv'
df_metab_name = pd.read_csv(excel_file_path)
df_metab_name = df_metab_name.rename(columns={'ChEBI_ID': 'chebi_id', 'Metabolite Name': 'metabo_name'})
# Load the metabolite synonyms
excel_file_path = 'metabolites_synonyms.csv'
df_metab_syn = pd.read_csv(excel_file_path)
df_metab_syn = df_metab_syn.rename(columns={'ChEBI_ID': 'chebi_id', 'Synonyms': 'synonym_value'})

# Create SQLAlchemy engine
engine = get_engine()

# Specify data types for columns
met_dtype = {'chebi_id': VARCHAR(255), 'metabo_name': VARCHAR(255)}
# Specify data types for columns
syn_dtype = {'chebi_id': VARCHAR(255), 'synonym_value': VARCHAR(255)}

# Write DataFrame to MySQL table: Replace previous table with new data
if args.mode == "scratch":
    with engine.connect() as connection:
        connection.execute("DELETE FROM Metabolites")
        connection.execute("DELETE FROM MetaboliteSynonym")
    df_metab_name.to_sql(name='Metabolites', con=engine, if_exists='replace', index=False, dtype=met_dtype)
    df_metab_syn.to_sql(name='MetaboliteSynonym', con=engine, if_exists='append', index=False, dtype=dtype)

# For duplicates, keep initial data
elif args.mode == "extras":
    existing_ids = pd.read_sql("SELECT chebi_id FROM Metabolites", con=engine)['chebi_id']
    filtered_df = df_metab_name[~df_metab_name['chebi_id'].isin(existing_ids)]
    filtered_df.to_sql(name='Metabolites', con=engine, if_exists='append', index=False, dtype=met_dtype)

# For duplicates, keep new data
elif args.mode == "replace":
    existing_df = pd.read_sql("SELECT * FROM Metabolites", con=engine)
    merged_df = pd.concat([existing_df, df_metab_name]).drop_duplicates(subset=['chebi_id'], keep='last')
    merged_df.to_sql(name='Metabolites', con=engine, if_exists='replace', index=False, dtype=met_dtype)

else:
    raise ValueError("Invalid mode selected. Please select from `scratch`, `extras`, or `replace`.")

# Close the engine
engine.dispose()

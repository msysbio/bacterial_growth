import os
import pandas as pd
import tomllib  #  Parses TOML files
from pathlib import Path
from sqlalchemy import create_engine, VARCHAR, text
import argparse

# Create the argument parser
parser = argparse.ArgumentParser(description="""Upload metabolites, ChEBI id, their names and their synonyms, and/or taxa,
                                 NCBI Taxonomy Ids and their preferred names, to the database corresponding tables.""",
                                 formatter_class=argparse.RawTextHelpFormatter)

# Add the `--mode` argument with predefined choices
mode_message = """Set the mode of your choice:
scratch: will drop all previous metabolites data and load new data; will fail if a table is empty, in this case, use `extras`.
extras: will keep the existing data as is, (even in the case of an empty table) and add only new data; in case of duplicates, the initial data will be kept (no updating).
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
    secrets_file = "../../config/database.toml"
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

# Get constraints of a MySQL table
def get_constraints(engine, table_name):
    """
    Get the foreign key constraints for a given table.
    :param engine: SQLAlchemy engine
    :param table_name: str
    :return: list of tuples
    """
    # Get the foreign keys from the information_schema
    with engine.connect() as connection:
        result = connection.execute(text(f"""
        SELECT CONSTRAINT_NAME
        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE TABLE_NAME = :table_name AND TABLE_SCHEMA = DATABASE()
        AND CONSTRAINT_NAME != 'PRIMARY'
        """), {'table_name': table_name}).fetchall()
    return result

# Drop constraints of a MySQL table
def drop_constraints(engine, table_name, constraints):
    """
    Drop the foreign key constraints.
    :param engine: SQLAlchemy engine
    :param constraints: list of tuples
    """
    with engine.connect() as connection:
        for row in constraints:
            foreign_key_name = row[0]
            try:
                connection.execute(text(f"ALTER TABLE {table_name} DROP FOREIGN KEY {foreign_key_name}"))
            except Exception as e:
                print(f"Error dropping constraint: {e}")
                pass

# Add constraints to a MySQL table
def add_constraints(engine, table_name, constraints, key):
    """
    Add the foreign key constraints.
    :param engine: SQLAlchemy engine
    :param constraints: list of tuples
    """
    print("Adding constraints back:", table_name)
    with engine.connect() as connection:
        for row in constraints:
            foreign_key_name = row[0]
            connection.execute(text(f"ALTER TABLE {table_name} ADD CONSTRAINT {foreign_key_name} FOREIGN KEY ({key}) REFERENCES {table_name}({key})"))

# Remove table's data and insert new data
def scratch_table_with_fk_check(engine, table_name, df, dtype, constraints_key):
    """
    Handle scratch operations for a table by disabling foreign key checks, performing operations,
    and then re-enabling foreign key checks.

    :param engine: SQLAlchemy engine
    :param table_name: str, table name
    :param df: DataFrame, data to insert into the table
    :param dtype: dict, column data types
    :param constraints_key: str, key column for constraints
    """
    if df is not None:
        print(f"Processing table: {table_name}")

        with engine.connect() as connection:
            # Disable foreign key checks to allow truncating and inserting data without constraint issues
            connection.execute(text("SET foreign_key_checks = 0"))

            try:
                # Truncate the table
                connection.execute(text(f"TRUNCATE TABLE {table_name}"))

                # Insert the data into the table
                df.to_sql(name=table_name, con=engine, if_exists='replace', index=False, dtype=dtype)

                # Optional: If you need to create indexes or perform additional SQL operations
                if table_name == 'Metabolites':
                    connection.execute(text("CREATE UNIQUE INDEX idx_chebi_id ON Metabolites(chebi_id)"))

            except Exception as e:
                print(f"Error during operations on {table_name}: {e}")
                # If an error occurs, you can log or handle it as needed
            finally:
                # Re-enable foreign key checks after the operations
                connection.execute(text("SET foreign_key_checks = 1"))

            # Add constraints back to the table
            constraints = get_constraints(engine, table_name)
            add_constraints(engine, table_name, constraints, constraints_key)

#
def replace_metabolites(engine, df_metab_name, df_metab_syn, chebi_ids):
    """
    Replace entries in the `Metabolites` table with updated data,
    ensuring associated synonyms are preserved or updated.
    """

    with engine.begin() as conn:
        # Step 1: Update existing rows in Metabolites
        for _, row in df_metab_name.iterrows():
            chebi_id = row['chebi_id']
            metabo_name = row['metabo_name']

            if chebi_id in chebi_ids:
                # Update existing row
                conn.execute(
                    text("UPDATE Metabolites SET metabo_name = :metabo_name WHERE chebi_id = :chebi_id"),
                    {"chebi_id": chebi_id, "metabo_name": metabo_name}
                )
            else:
                # Insert new row if it doesn't exist
                conn.execute(
                    text("INSERT INTO Metabolites (chebi_id, metabo_name) VALUES (:chebi_id, :metabo_name)"),
                    {"chebi_id": chebi_id, "metabo_name": metabo_name}
                )

        # Step 2: Update or insert synonyms
        for _, row in df_metab_syn.iterrows():
            chebi_id = row['chebi_id']
            synonym_value = row['synonym_value']

            # Check if synonym already exists for the chebi_id
            existing = conn.execute(
                text("SELECT 1 FROM MetaboliteSynonym WHERE chebi_id = :chebi_id AND synonym_value = :synonym_value"),
                {"chebi_id": chebi_id, "synonym_value": synonym_value}
            ).fetchone()

            if not existing:
                # Insert new synonym if it doesn't already exist
                conn.execute(
                    text("INSERT INTO MetaboliteSynonym (chebi_id, synonym_value) VALUES (:chebi_id, :synonym_value)"),
                    {"chebi_id": chebi_id, "synonym_value": synonym_value}
                )

    print("Replace operation completed successfully.")



# Initialize dfs
df_metab_name = df_metab_syn = df_taxa = None

# Load the metabolites
mets_file_path = 'metabolites/metabolites.csv'
if os.path.exists(mets_file_path):
    df_metab_name = pd.read_csv(mets_file_path)
    df_metab_name = df_metab_name.rename(columns={'ChEBI_ID': 'chebi_id', 'Metabolite Name': 'metabo_name'}).dropna()

# Load the metabolite synonyms
met_syn_file_path = 'metabolites/metabolites_synonyms.csv'
if os.path.exists(met_syn_file_path):
    df_metab_syn = pd.read_csv(met_syn_file_path)
    df_metab_syn = df_metab_syn.rename(columns={'ChEBI_ID': 'chebi_id', 'Synonyms': 'synonym_value'}).dropna()

# Load the taxa names and ids
taxa_file_path = 'taxa/unicellular_ncbi_ids_preferred_names.tsv'
if os.path.exists(taxa_file_path):
    df_taxa = pd.read_csv(taxa_file_path, sep="\t", header=None).dropna()
    df_taxa.columns = ['tax_id', 'tax_names']

# Create SQLAlchemy engine
engine = get_engine()
# Specify data types for columns for metabolite names
met_dtype = {'chebi_id': VARCHAR(255), 'metabo_name': VARCHAR(255)}
# Specify data types for columns for metabolite synonyms
syn_dtype = {'chebi_id': VARCHAR(255), 'synonym_value': VARCHAR(255)}
# Specify data types for columns for taxa
taxa_dtype = {'tax_id': VARCHAR(255), 'tax_names': VARCHAR(255)}

# Write DataFrame to MySQL table: Replace previous table with new data
if args.mode == "scratch":

    print("SCRATCH MODE")

    # Define table configurations
    table_configs = [
        {
            'name': 'Metabolites',
            'df': df_metab_name,
            'dtype': met_dtype,
            'key': 'chebi_id',
            'additional_sql': "CREATE UNIQUE INDEX idx_chebi_id ON Metabolites(chebi_id)"
        },
        {
            'name': 'MetaboliteSynonym',
            'df': df_metab_syn,
            'dtype': syn_dtype,
            'key': 'chebi_id',
            'additional_sql': None
        },
        {
            'name': 'Taxa',
            'df': df_taxa,
            'dtype': taxa_dtype,
            'key': 'chebi_id',
            'additional_sql': None
        }
    ]

    for config in table_configs:
        if config['df'] is not None:
            scratch_table_with_fk_check(engine, config['name'], config['df'], config['dtype'], config['key'])
            if config['additional_sql']:
                with engine.connect() as connection:
                    connection.execute(text(config['additional_sql']))

# For duplicates, keep initial data
elif args.mode == "extras":
    print("EXTRAS MODE")
    if df_metab_name is not None and df_metab_syn is not None:
        print("Loading metabolite names")
        existing_mets = pd.read_sql("SELECT chebi_id FROM Metabolites", con=engine)['chebi_id']
        filtered_df = df_metab_name[~df_metab_name['chebi_id'].isin(existing_mets)]
        filtered_df.to_sql(name='Metabolites', con=engine, if_exists='append', index=False, dtype=met_dtype)

        print("Loading metabolite synonyms")
        existing_syns = pd.read_sql("SELECT chebi_id FROM MetaboliteSynonym", con=engine)['chebi_id']
        filtered_df = df_metab_syn[~df_metab_syn['chebi_id'].isin(existing_syns)]
        filtered_df.to_sql(name='MetaboliteSynonym', con=engine, if_exists='append', index=False, dtype=met_dtype)

    if df_taxa is not None:
        print("Loading taxa")
        existing_taxa = pd.read_sql("SELECT tax_id FROM Taxa", con=engine)['tax_id']
        filtered_df = df_taxa[~df_taxa['tax_id'].isin(existing_taxa)]
        filtered_df.to_sql(name='Taxa', con=engine, if_exists='append', index=False, dtype=taxa_dtype)

# For duplicates, keep new data
elif args.mode == "replace":

    print("REPLACE MODE")
    chebi_ids = tuple(df_metab_name['chebi_id'].unique())
    replace_metabolites(engine, df_metab_name, df_metab_syn, chebi_ids)

    if df_taxa is not None:
        print("Loading taxa")
        existing_df = pd.read_sql_table('Taxa', con=engine)
        new_df = pd.concat([existing_df, df_taxa]).drop_duplicates()
        new_df.to_sql(name='Taxa', con=engine, if_exists='replace', index=False)

else:
    raise ValueError("Invalid mode selected. Please select from `scratch`, `extras`, or `replace`.")

# Close the engine
engine.dispose()

# Aim:
#   Add chebi ids and their names in the metabolitename table
# Usage:
#   python populate_metadb.py
# Notes:
#   Make sure you have the secrets.toml file


import pandas as pd
import mysql.connector
import sqlalchemy
from sqlalchemy import create_engine, VARCHAR

excel_file_path = 'metabolites_TABLE1.csv'
df_metab_name = pd.read_csv(excel_file_path)
df_metab_name = df_metab_name.rename(columns={'ChEBI_ID': 'cheb_id', 'Metabolite Name': 'metabo_name'})

# Define the MySQL connection string
def get_connection():

    secrets_file = "../../../app/.streamlit/secrets.toml"
    secrets = [line.strip() for line in open(secrets_file, 'r').readlines() if line.strip()]
    secrets_dict = dict(line.split(' = ', 1) for line in secrets[1:])

    user = secrets_dict["username"].replace('"', '')
    password = secrets_dict["password"].replace('"', '')
    host = secrets_dict["host"].replace('"', '')
    port = 3306
    database = secrets_dict["database"].replace('"', '')

    return create_engine(
        url="mysql+pymysql://{0}:{1}@{2}:{3}/{4}".format(
            user, password, host, port, database
        )
)

# Create SQLAlchemy engine
engine = get_connection()

# Specify data types for columns
dtype = {'cheb_id': VARCHAR(255), 'metabo_name': VARCHAR(255)}

# Write DataFrame to MySQL table
df_metab_name.to_sql(name='Metabolites', con=engine, if_exists='append', index=False, dtype=dtype)

# Close the engine
engine.dispose()

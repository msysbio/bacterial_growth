import pandas as pd
import mysql.connector
import sqlalchemy
from sqlalchemy import create_engine, VARCHAR
from populate_metadb import get_connection

excel_file_path = 'metabolites_TABLE2.csv'
df_metab_syn = pd.read_csv(excel_file_path)
df_metab_syn = df_metab_syn.rename(columns={'ChEBI_ID': 'cheb_id', 'Synonyms': 'synonym_value'})

# Create SQLAlchemy engine
engine = get_connection()

# Specify data types for columns
dtype = {'cheb_id': VARCHAR(255), 'synonym_value': VARCHAR(255)}

# Write DataFrame to MySQL table
df_metab_syn.to_sql(name='MetaboliteSynonym', con=engine, if_exists='append', index=False, dtype=dtype)

# Close the engine
engine.dispose()

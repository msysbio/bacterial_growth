import pandas as pd
from sqlalchemy import create_engine, VARCHAR
import os, sys
current_dir = os.path.dirname(os.path.realpath(__file__))
src_dir = os.path.dirname(current_dir)
sys.path.append(src_dir)
from constants import *

excel_file_path = '../bash_scripts/metabolites/metabolites_TABLE1.csv'
df_metab_syn = pd.read_csv(excel_file_path)



# Define the MySQL connection string
conn_string = f'mysql+mysqlconnector://{USER}:{PASSWORD}@{HOST}/{DATABASE}'


df_metab_name = pd.read_csv(excel_file_path)

df_metab_name = df_metab_name.rename(columns={'ChEBI_ID': 'cheb_id', 'Metabolite Name': 'metabo_name'})


# Create SQLAlchemy engine
engine = create_engine(conn_string)

# Specify data types for columns
dtype = {'cheb_id': VARCHAR(255), 'metabo_name': VARCHAR(255)}
# Write DataFrame to MySQL table
df_metab_name.to_sql(name='Metabolites', con=engine, if_exists='append', index=False, dtype=dtype)

# Close the engine
engine.dispose()

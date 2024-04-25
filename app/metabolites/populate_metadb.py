import pandas as pd
import mysql.connector
import sqlalchemy
from sqlalchemy import create_engine, VARCHAR

excel_file_path = 'C:/Users/sofia/OneDrive - KU Leuven/THESIS/metabolites/metabolites_TABLE1.csv'
df_metab_name = pd.read_csv(excel_file_path)

df_metab_name = df_metab_name.rename(columns={'ChEBI_ID': 'cheb_id', 'Metabolite Name': 'metabo_name'})

# Define the MySQL connection string
conn_string = 'mysql+mysqlconnector://root:Amartemucho123-@localhost/Metabolites'

# Create SQLAlchemy engine
engine = create_engine(conn_string)

# Specify data types for columns
dtype = {'cheb_id': VARCHAR(255), 'metabo_name': VARCHAR(255)}
# Write DataFrame to MySQL table
df_metab_name.to_sql(name='metabolitename', con=engine, if_exists='append', index=False, dtype=dtype)

# Close the engine
engine.dispose()

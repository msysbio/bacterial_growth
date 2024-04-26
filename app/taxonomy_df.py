import pandas as pd
import json
from sqlalchemy import create_engine, VARCHAR

# Define the path to your names.dmp file
names_file_path = "/Users/sofia/Desktop/bacterial_growth/src/names.dmp"

# Define column names for the DataFrame
columns = ["tax_id", "tax_names"]

# Initialize an empty list to store parsed data
parsed_data = []

# Read the names.dmp file line by line and parse relevant information
with open(names_file_path, "r") as file:
    for line in file:
        line_data = line.strip().split("|")
        parsed_data.append({
            "tax_id": int(line_data[0].strip()),
            "tax_names": line_data[1].strip(),
        })

# Convert the parsed data into a pandas DataFrame
df = pd.DataFrame(parsed_data, columns=columns)
#df = df.drop_duplicates(subset=['tax_id'])
#print(len(df))
# Now df contains the parsed data from the names.dmp file
#print(df.head())

df.to_csv("taxonomy_names.csv", index=False)


# Read the filter_ids.tsv file into a DataFrame
filter_ids_df = pd.read_csv('/Users/sofia/Desktop/bacterial_growth/src/unicellular_ncbi_2023.tsv', sep="\t", header=None, names=["tax_id"])
unique_rows = filter_ids_df.drop_duplicates(subset=['tax_id'])
print(len(unique_rows))

# Merge the two DataFrames on tax_id to filter names
filtered_names_df = df[df["tax_id"].isin(unique_rows["tax_id"])]
filtered_names_unique_df = filtered_names_df.drop_duplicates(subset="tax_id")
filtered_names_unique_df = filtered_names_unique_df.drop_duplicates(subset='tax_names')
print(len(filtered_names_unique_df))

# Define the MySQL connection string
conn_string = 'mysql+mysqlconnector://root:Amartemucho123-@localhost/BacterialGrowth'

# Create SQLAlchemy engine
engine = create_engine(conn_string)

# Specify data types for columns
dtype = {'tax_id': VARCHAR(255), 'tax_names': VARCHAR(255)}
# Write DataFrame to MySQL table
filtered_names_unique_df.to_sql(name='taxa', con=engine, if_exists='append', index=False, dtype=dtype)

# Close the engine
engine.dispose()
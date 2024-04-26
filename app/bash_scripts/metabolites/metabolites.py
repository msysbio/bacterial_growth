#%%%
# Creation of the metabolite list to use in the ref_db

import re
import pandas as pd
import requests
from bioservices import *  # The ChEBI() class, an Interface for CheBI, is part of the bioservices library
# predefined list of metabolites
import pandas as pd

#%%% Methods
chebi = ChEBI()
def get_syn(chebi_id):
      if pd.isna(chebi_id):
        return None

      search_results = chebi.getCompleteEntity(chebi_id)
      if search_results and hasattr(search_results, 'Synonyms'):
         syn_list = search_results.Synonyms
         syn = [str(item['data'].lower()) for item in syn_list]
         return syn
      else:
         return None

def get_AsciiName(chebi_id):

    if pd.isna(chebi_id):
       return None

    search_results = chebi.getCompleteEntity(chebi_id)
    if search_results:
        return search_results.chebiAsciiName
    else:
         return None


def get_IUPACC(chebi_id):
      if pd.isna(chebi_id):
        return None

      search_results = chebi.getCompleteEntity(chebi_id)
      if search_results and hasattr(search_results, 'IupacNames'):
         iupacc_list = search_results.IupacNames
         iupacc = [str(item['data'].lower()) for item in iupacc_list]
         return iupacc
      else:
         return None

def add_to_syn(row):
    ascii_value = row['AsciiName']
    syn_list = row['Synonyms']
    metab_value = row['metabolites']
    syn_set = []
    if isinstance(syn_list, list):
        syn_set = list(set(syn_list))

        if metab_value != ascii_value and metab_value not in syn_set:
            syn_set.append(metab_value)
        else:
            try:
                syn_set.remove(metab_value)
            except:
                pass
    return syn_set

#%%% Raes list   --  not to be used
file_metabo = 'Supplementary_Data_1_metabolites.txt'

with open(file_metabo, 'r') as file:
    data = file.read()

# Extract metabolites from predifined metabolite list
matches_metabo = re.findall(r'\[([^\]]+)\]', data)
#split_matches = [word.strip().lower() for match in matches_metabo for word in match.split(', ') for word in match.split(',')]
split_matches = [word.strip().lower() for match in matches_metabo for word in re.split(r',\s+', match)]
df = pd.DataFrame({'metabolites': split_matches})
df_unique = pd.DataFrame({'metabolites':df['metabolites'].unique()})

excel_file_path = 'metabolites_output.xlsx'
df_unique.to_excel(excel_file_path, index=False)

excel_curated_path = 'metabolites_curated2.xlsx'
df_curated = pd.read_excel(excel_curated_path)


chebi = ChEBI()
search_results = chebi.getLiteEntity("caffeine", maximumResults=1)
c=search_results[0].chebiId
a=chebi.getCompleteEntity("CHEBI:10102")
print(c)

def get_chebi_id(metabolite_name):
    search_results = chebi.getLiteEntity(metabolite_name, maximumResults=1)
    if search_results:
     return search_results[0].chebiId
    else:
        return None

df_curated['ChEBI_ID'] = df_curated['metabolites'].apply(get_chebi_id)

df_curated['Synonyms'] = df_curated['ChEBI_ID'].apply(get_syn)

df_curated['AsciiName'] = df_curated['ChEBI_ID'].apply(get_AsciiName)

df_curated['Iupac Names'] = df_curated['ChEBI_ID'].apply(get_IUPACC)

excel_file_path = 'metabolites_complete_syn.xlsx'
df_curated.to_excel(excel_file_path, index=False)

# %%% MCO Ontology
# This chunk of code will take up to 10 minutes to run

# Load the OWL file as text
with open("mco.owl", "r") as file:
    owl_text = file.read()

# Define a regex pattern for CHEBI IDs
chebi_pattern = re.compile(r'http://purl.obolibrary.org/obo/CHEBI_(\d+)')

# Find all matches in the OWL text
chebi_matches = chebi_pattern.findall(owl_text)

uniq_chebi = set(chebi_matches)
unique_chebi_list = list(uniq_chebi)
prefix_chebid = ["CHEBI:" + term for term in unique_chebi_list]

df_mco = pd.DataFrame({'ChEBI_ID': prefix_chebid})
df_mco['Synonyms'] = df_mco['ChEBI_ID'].apply(get_syn)
df_mco['AsciiName'] = df_mco['ChEBI_ID'].apply(get_AsciiName)
df_mco['Iupac Names'] = df_mco['ChEBI_ID'].apply(get_IUPACC)
df_mco['metabolites'] = df_mco['AsciiName']
# union_metab_df = pd.concat([df_mco, df_curated]).drop_duplicates(subset='ChEBI_ID')
union_metab_df = df_mco.drop_duplicates(subset='ChEBI_ID')

# %%
excel_file_path = 'metabolites_union.xlsx'
union_metab_df.to_excel(excel_file_path, index=False)
# %%
#union_metab_df['Synonyms'] = union_metab_df['Synonyms'].fillna('[]')
#df_union['Synonyms'] = df_union['Synonyms'].apply(ast.literal_eval)

# simplyfing the df in only just 3 columns, chEBI_ID, metabolite and synonyms
df_dup_union = union_metab_df.copy()
df_dup_union['metabolites'] = df_dup_union['metabolites'].str.lower()
df_dup_union['AsciiName'] = df_dup_union['AsciiName'].str.lower()

# Apply the function to each row
df_dup_union['Synonyms'] = df_dup_union.apply(add_to_syn, axis=1)

# Use asciiname and synonyms for the DB
#print(df_dup_union[df_dup_union.duplicated(subset=['AsciiName'], keep=False)]['AsciiName'].unique())
# %%
df_single_syn = df_dup_union.explode('Synonyms')

# %%
# DATAFRAME FOR TABLE 1: METABOLITES NAMES
df_metab_name=pd.DataFrame({'ChEBI_ID': df_dup_union['ChEBI_ID']})
df_metab_name['Metabolite Name'] = df_dup_union['AsciiName']

excel_file_path = 'metabolites_TABLE1.csv'
df_metab_name.to_csv(excel_file_path, index=False)
# %%
# DATAFREME FOR TABLE 2: METABOLITES SYNONYMS

df_metab_syn = pd.DataFrame({'ChEBI_ID': df_single_syn['ChEBI_ID']})
df_metab_syn['Synonyms'] = df_single_syn['Synonyms']
df_metab_syn = df_metab_syn.dropna(subset=['Synonyms'])

excel_file_path = 'metabolites_TABLE2.csv'
df_metab_syn.to_csv(excel_file_path, index=False)

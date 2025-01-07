#%%% Load libraries
import re
import pandas as pd
import argparse
# The ChEBI() class, an Interface for CheBI, is part of the bioservices library
from bioservices import *
import sys
import os
# Get the path two levels up
two_levels_up = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert(0, two_levels_up)
from utils import isFile

# %% Args
parser = argparse.ArgumentParser(description= "Script to build metabolites.csv and metabolites_synonyms.csv files from the MCO ontology and any other custom file.",
                                 formatter_class=argparse.RawTextHelpFormatter)

# Add a flag argument
parser.add_argument("--mco", action="store_true", help="Use the Raes lab dataset, too.")
parser.add_argument("--raes", action="store_true", help="Use the Raes lab dataset, too.")
parser.add_argument("--other", type=isFile, help="Use custom file with metabolites.")

# Parse the arguments
args = parser.parse_args()

if not any([args.mco, args.raes, args.other]):
    raise ValueError("At least one of the `mco`, `raes`, `other` flags should be used.")


#%%% Methods

# We will use the ChEBI class (https://bioservices.readthedocs.io/en/latest/_modules/bioservices/chebi.html) of the
# bioservices library to interact with the ChEBI database.
def get_syn(chebi_id):
    """Get the synonyms of a ChEBI ID"""
    chebi = ChEBI()
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
    chebi = ChEBI()
    """Get the AsciiName of a ChEBI ID"""
    if pd.isna(chebi_id):
       return None
    search_results = chebi.getCompleteEntity(chebi_id)
    if search_results:
        return search_results.chebiAsciiName
    else:
         return None


def get_IUPACC(chebi_id):
    """Get the IUPAC name of a ChEBI ID"""
    chebi = ChEBI()
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
    """Add synonyms if their ASCII id is not already there"""
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


def get_chebi_id(metabolite_name):
    """Get the ChEBI ID of a metabolite"""
    chebi = ChEBI()
    search_results = chebi.getLiteEntity(metabolite_name, maximumResults=1)
    if search_results:
     return search_results[0].chebiId
    else:
        return None


#%%% Raes list   --  not to be used
df_raes = df_mco = df_other = None
if args.raes:
    # [NOTE] All metabolites mentioned in the Raes file are included in the MCO. Therefore, we will not use this list.
    print("Processing Raes lab dataset.")
    file_metabo = 'Supplementary_Data_1_metabolites.txt'
    with open(file_metabo, 'r') as f:
       data = f.read()
    matches_metabo = re.findall(r'\[([^\]]+)\]', data)
    split_matches = [word.strip().lower() for match in matches_metabo for word in re.split(r',\s+', match)]
    df = pd.DataFrame({'metabolites': split_matches})
    df_raes = pd.DataFrame({'metabolites':df['metabolites'].unique()})

    df_raes['ChEBI_ID'] = df_raes['metabolites'].apply(get_chebi_id)
    df_raes['Synonyms'] = df_raes['ChEBI_ID'].apply(get_syn)
    df_raes['AsciiName'] = df_raes['ChEBI_ID'].apply(get_AsciiName)
    df_raes['Iupac Names'] = df_raes['ChEBI_ID'].apply(get_IUPACC)
    print("Raes lab dataset processed.")

# %%% MCO Ontology
if args.mco:
    print("Processing MCO ontology.")
    # [NOTE] This chunk of code will take up to 10 minutes to run
    with open("mco.owl", "r") as owlfile:
        owl_text = owlfile.read()

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
    print("MCO ontology processed.")

# Load custom file
if args.other:
    print("Processing custom file.")
    df_other = pd.read_csv(args.other)
    if df_other.shape[1] > 1:
        raise ValueError("The file should have only one column")
    df_other.columns = ["metabolites"]
    df_other['ChEBI_ID'] = df_other['metabolites'].apply(get_chebi_id)
    df_other['Synonyms'] = df_other['ChEBI_ID'].apply(get_syn)
    df_other['AsciiName'] = df_other['ChEBI_ID'].apply(get_AsciiName)
    df_other['Iupac Names'] = df_other['ChEBI_ID'].apply(get_IUPACC)
    print("Custom file processed.")

# %% Merge dfs built from the MCO and/or the Raes and/or the custom files
dfs = [df for df in [df_mco, df_raes, df_other] if df is not None]
for i in range(len(dfs)):
    dfs[i].to_csv(f"df_{i}.csv", index=False)

union_metab_df = pd.concat(dfs).drop_duplicates(subset='ChEBI_ID')
df_dup_union = union_metab_df.copy()

# Continue as it used to be .......................
df_dup_union['metabolites'] = df_dup_union['metabolites'].str.lower()
df_dup_union['AsciiName'] = df_dup_union['AsciiName'].str.lower()

# Apply the function to each row
df_dup_union['Synonyms'] = df_dup_union.apply(add_to_syn, axis=1)

# Use asciiname and synonyms for the DB
df_single_syn = df_dup_union.explode('Synonyms')

# %% Export dataframes to csv files
# DATAFRAME FOR TABLE 1: METABOLITES NAMES
df_metab_name = pd.DataFrame({'ChEBI_ID': df_dup_union['ChEBI_ID']})
df_metab_name['Metabolite Name'] = df_dup_union['AsciiName']
excel_file_path = 'metabolites.csv'
df_metab_name.to_csv(excel_file_path, index=False)

# DATAFREME FOR TABLE 2: METABOLITES SYNONYMS
df_metab_syn = pd.DataFrame({'ChEBI_ID': df_single_syn['ChEBI_ID']})
df_metab_syn['Synonyms'] = df_single_syn['Synonyms']
df_metab_syn = df_metab_syn.dropna(subset=['Synonyms'])

excel_file_path = 'metabolites_synonyms.csv'
df_metab_syn.to_csv(excel_file_path, index=False)


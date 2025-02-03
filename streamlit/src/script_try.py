from parse_raw_data import get_techniques_metabolites 
from parse_raw_data import get_measures_growth
from parse_raw_data import get_measures_abundances
import pandas as pd
from constants import LOCAL_DIRECTORY

template_filename = LOCAL_DIRECTORY + 'template_raw_data_ex.xlsx'
list_growth = ['Optical Density (OD)','16S rRNA-seq']
list_metabolites = ['glucose']
errors = []
errors = get_techniques_metabolites(list_growth, list_metabolites, template_filename)
print(errors)
measures, metabos = get_measures_growth(template_filename)
print(measures)
print(metabos)
abundances_per_replicate = get_measures_abundances(template_filename)
print(abundances_per_replicate)
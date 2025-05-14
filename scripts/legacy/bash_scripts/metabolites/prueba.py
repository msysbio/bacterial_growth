import re
import pandas as pd
import requests


def get_chebi_id_from_name(metabolite_name,searchCategory, maximumResults, stars):
    base_url = "https://www.ebi.ac.uk/webservices/chebi/2.0/getLiteEntity"
    params = {
        'name': metabolite_name,
        'searchCategory': searchCategory,
        'maximumResults': maximumResults,
        'stars' : stars,
        'format': 'json'
    }

    response = requests.get(base_url, params=params)
    print(response) 

    if response.status_code == 200:
        data = response.json()
        if 'chebiLiteEntity' in data:
            chebi_id = data['chebiLiteEntity'][0]['chebiId']
            return chebi_id
        else:
            return None
    else:
        print(f"Error: Unable to fetch data for metabolite {metabolite_name}.")
        return None

# Example usage
metabolite_name = "caffeine"  # Replace this with the metabolite name you want to query
chebi_id = get_chebi_id_from_name(metabolite_name, searchCategory="ALL", maximumResults=1, stars="ALL")
print(chebi_id)
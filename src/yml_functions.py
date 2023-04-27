import yaml

from constants import *

yaml.Dumper.ignore_aliases = lambda self, data: True

def read_yml(file):
    """ 
    A function to read yml file
    
    :param file: yml
    :return info (if ok)
    """
    try:
        with open(file) as f:
            info = yaml.safe_load(f)
        return info
    except yaml.YAMLError as exc:
        print('\n\tERROR: Check your YAML file, maybe you used forbidden characters (i.e., :)\n')
        exit()

def write_yml(data, yml_file):
    """ 
    A function to write yml file
    
    :param data to write
    :param wml_file path
    """
    with open(yml_file, "w") as file:
        file.write('# New data to populate the DB\n# Substitute the null values with your data\n# Do not modify the indentation or remove any field, even if you do not have data for it\n')
        yaml.dump(data, file, Dumper=yaml.Dumper,sort_keys=False,indent=2)

def createStudyYml(num_biological_replicates, num_perturbations):
    """
    Create the study yml file for the user to fill in

    :param num_biological_replicates, num_perturbations: int
    """
    yml_dict = {}
    yml_dict = addStudyYml(yml_dict)
    yml_dict = addBiologicalReplicateYml(yml_dict, num_biological_replicates)
    yml_dict = addPerturbationYml(yml_dict, num_perturbations)

    write_yml(yml_dict, LOCAL_DIRECTORY+'yml_files/study_information_tmp.yml')

def createBiologicalReplicateYml(study_id, num_biological_replicates, num_perturbations):
    """
    Create the biological replicate yml file for the user to fill in

    :param study_id, num_biological_replicates, num_perturbations: int
    """
    yml_dict = {}
    yml_dict['STUDY_ID'] = study_id
    yml_dict = addBiologicalReplicateYml(yml_dict, num_biological_replicates)
    yml_dict = addPerturbationYml(yml_dict, num_perturbations)

    write_yml(yml_dict, LOCAL_DIRECTORY+'yml_files/biological_replicate_information_tmp.yml')

def createPerturbationYml(study_id, biological_id, num_perturbations):
    """
    Create the perturbation yml file for the user to fill in

    :param study_id, biological_id, num_perturbations: int
    """
    yml_dict = {}
    yml_dict['STUDY_ID'] = study_id
    yml_dict['BIOLOGICAL_ID'] = biological_id
    yml_dict = addPerturbationYml(yml_dict, num_perturbations)

    write_yml(yml_dict, LOCAL_DIRECTORY+'yml_files/perturbation_information_tmp.yml')

def createReplicatesYml(study_id, biological_id, perturbation_id):
    """
    Create the replicates yml file for the user to fill in

    :param study_id, biological_id, perturbation_id: int
    """
    yml_dict = {}
    yml_dict['STUDY_ID'] = study_id
    yml_dict['BIOLOGICAL_ID'] = biological_id
    yml_dict['PERTURBATION_ID'] = perturbation_id
    yml_dict['FILES'] = None

    write_yml(yml_dict, LOCAL_DIRECTORY+'yml_files/replicates_information_tmp.yml')

def addStudyYml(final_dict):
    '''
    Add study dictionary to final_dict

    :param and return final_dict
    '''
    study_dict = {'NAME': None,
                  'DESCRIPTION': None
                  }
    
    final_dict['STUDY'] = []
    final_dict['STUDY'].append(study_dict)
    
    return final_dict

def addBiologicalReplicateYml(final_dict, num_biological_replicates):
    '''
    Add biological replicate dictionary to final_dict

    :param and return final_dict
    :param num_biological_replicates: int. It will add as much dicts as num_biological_replicates
    '''
    reactor_dict = {
        'NAME': {'value': None, 'description': 'Name of the reactor'}, 
        'VOLUME': {'value': None, 'description': 'Volume in mL'},
        'ATMOSPHERE': {'value': None, 'description': 'Atmospheres in XXX'},
        'STIRRING_SPEED': {'value': None, 'description': 'Speed in rpm'},
        'MODE': {'value': None, 'description': 'chemostat/batch/fed-batch'},
        'DESCRIPTION': {'value': None, 'description': 'Description of the reactor'}
        }
    biol_rep_dict = {
        # 'BIOLOGICAL_REPLICATE_NUMBER': 0,
        'NAME': {'value': None, 'description': 'Name of the biological replicate'},
        'REACTOR': reactor_dict,
        'PLATE': {'ID': {'value': None, 'description': 'Number of plate'}, 'COLUMN': {'value': None, 'description': 'Indicated in numbers'}, 'ROW': {'value': None, 'description': 'Indicated in letters'}},
        'MEDIA': {'NAME': {'value': None, 'description': 'Name of the media'}, 'MEDIA_PATH': {'value': None, 'description': 'File path containing the media description'}},
        'BACTERIA': [{'GENUS': None, 'SPECIES': None, 'STRAIN': None},{'GENUS': None, 'SPECIES': None, 'STRAIN': None}],
        'BLANK': {'value': None, 'description': 'Boolean (numerical). 1 if the biological replicate is blank. 0 otherwise.'},
        'INOCULUM_CONCENTRATION': {'value': None, 'description': 'Indicated in cells per mL'},
        'INOCULUM_VOLUME': {'value': None, 'description': 'Indicate in mL'},
        'INITIAL_PH': None,
        'INITIAL_TEMPERATURE': {'value': None, 'description': 'Indicated in Celsius'},
        'CARBON_SOURCE': {'value': None, 'description': 'Boolean (numerical). 1 if the carbon source present. 0 otherwise.'},
        'ANTIBIOTIC': {'value': None, 'description': 'Boolean (numerical). 1 if antibiotic present. 0 otherwise.'},
        'DESCRIPTION': {'value': None, 'description': 'Description of the biological replicate'},
        'FILES': {'value': None, 'description': 'Directory with the files corresponding to this biological replicate.'}
        }

    if num_biological_replicates > 0: final_dict['BIOLOGICAL_REPLICATE'] = []
    for i in range(num_biological_replicates):
        # biol_rep_dict['BIOLOGICAL_REPLICATE_NUMBER'] = i+1
        final_dict['BIOLOGICAL_REPLICATE'].append(biol_rep_dict)
    
    return final_dict

def addPerturbationYml(final_dict, num_perturbations):
    '''
    Add perturbation dictionary to final_dict

    :param and return final_dict
    :param num_perturbations: int. It will add as much dicts as num_perturbations
    '''
    pert_dict = {
        'PLATE': {'ID': {'value': None, 'description': 'Number of plate'}, 'COLUMN': {'value': None, 'description': 'Indicated in numbers'}, 'ROW': {'value': None, 'description': 'Indicated in letters'}},
        'PROPERTY': {'value': None, 'description': 'Indicate which property has been perturbed'},
        'NEW_VALUE': {'value': None, 'description': 'New value of the perturbed property'},
        'STARTING_TIME': {'value': None, 'description': 'Time in minutes'},
        'ENDING_TIME': {'value': None, 'description': 'Time in minutes'},
        'DESCRIPTION': {'value': None, 'description': 'Description of the perturbation'},
        'FILES': {'value': None, 'description': 'Directory with the files corresponding to this perturbation.'}
        }
    
    if num_perturbations > 0: final_dict['PERTURBATION'] = []
    for i in range(num_perturbations):
        final_dict['PERTURBATION'].append(pert_dict)
    
    return final_dict

def getBiologicalReplicateInfo(file):
    """
    Get info from yml biological replicate file
    
    :param file
    :return dictionary
    """
    with open(file, 'r') as f:
        info = yaml.safe_load(f)

        biological_replicate = {
            'biologicalReplicateName': info['biological_replicate']['name'],
            'biologicalReplicateDate': info['biological_replicate']['date'],
            'biologicalReplicateAuthor': info['biological_replicate']['author'],
            'biologicalReplicateDescription': info['biological_replicate']['description']
        }
        
        biological_replicate_filtered = {k: v for k, v in biological_replicate.items() if v is not None}
        return biological_replicate_filtered
    
def getCultivationInfo(file):
    """
    Get info from yml biological replicate file
    
    :param file
    :return dictionary
    """
    with open(file, 'r') as f:
        info = yaml.safe_load(f)

        cultivation = {
            'inoculumConcentration': info['cultivation']['inoculum_concentration'],
            'inoculumVolume': info['cultivation']['inoculum_volume'],
            'initialPh': info['cultivation']['initial_ph'],
            'initialTemperature': info['cultivation']['initial_temperature'],
            'carbonSource': info['cultivation']['carbon_source'],
            'antibiotic': info['cultivation']['antibiotic'],
            'cultivationDescription': info['cultivation']['description']
        }
        
        cultivation_filtered = {k: v for k, v in cultivation.items() if v is not None}

        if 'carbonSource' in cultivation_filtered:
            if cultivation_filtered['carbonSource'] == True:
                cultivation_filtered['carbonSource'] = 1
            else:
                cultivation_filtered['carbonSource'] = 0
        
        return cultivation_filtered
import yaml

yaml.Dumper.ignore_aliases = lambda self, data: True

def read_yml(file):
    """ A function to read yml file"""
    with open(file) as f:
        info = yaml.safe_load(f)
    return info

def write_yml(data, yml_file):
    """ A function to write yml file"""
    with open(yml_file, "w") as file:
        file.write('# New data to populate the DB\n# Substitute the null values with your data\n# Do not modify the indentation or remove any field, even if you do not have data for it\n')
        yaml.dump(data, file, Dumper=yaml.Dumper,sort_keys=False,indent=2)
    print('\n\n{} file created!'.format(yml_file))

def createStudyYml(num_experiments, num_perturbations, **files_dir):
    yml_dict = {}
    yml_dict = addStudyYml(yml_dict)
    yml_dict = addExperimentYml(yml_dict, num_experiments)
    yml_dict = addPerturbationYml(yml_dict, num_perturbations)
    # yml_dict['FILES'] = files_dir

    write_yml(yml_dict, 'yml_info_files/study_information_tmp.yml')

def createExperimentYml(study_id, num_experiments, num_perturbations, **files_dir):
    yml_dict = {}
    yml_dict['STUDY_ID'] = study_id
    yml_dict = addExperimentYml(yml_dict, num_experiments)
    yml_dict = addPerturbationYml(yml_dict, num_perturbations)
    # yml_dict['FILES'] = files_dir

    write_yml(yml_dict, 'yml_info_files/experiment_information_tmp.yml')

def createPerturbationYml(study_id, experiment_id, num_perturbations, **files_dir):
    yml_dict = {}
    yml_dict['STUDY_ID'] = study_id
    yml_dict['EXPERIMENT_ID'] = experiment_id
    yml_dict = addPerturbationYml(yml_dict, num_perturbations)
    # yml_dict['FILES'] = files_dir

    write_yml(yml_dict, 'yml_info_files/perturbation_information_tmp.yml')

def createReplicatesYml(study_id, experiment_id, perturbation_id, **files_dir):
    yml_dict = {}
    yml_dict['STUDY_ID'] = study_id
    yml_dict['EXPERIMENT_ID'] = experiment_id
    yml_dict['PERTURBATION_ID'] = perturbation_id
    yml_dict['FILES'] = None

    write_yml(yml_dict, 'yml_info_files/replicates_information_tmp.yml')

def addStudyYml(final_dict):
    study_dict = {'NAME': None,
                  'STUDY_DESCRIPTION': None
                  }
    
    final_dict['STUDY'] = []
    final_dict['STUDY'].append(study_dict)
    
    return final_dict

def addExperimentYml(final_dict, num_experiments):
    exp_dict = {
        # 'EXPERIMENT_NUMBER': 0,
        'NAME': {'value': None, 'description': 'Name of the experiment'},
        'REACTOR': {'NAME': {'value': None, 'description': 'Name of the reactor'}, 'VOLUME': {'value': None, 'description': 'Volume in mL'}},
        'PLATE': {'ID': {'value': None, 'description': 'Number of plate'}, 'COLUMN': {'value': None, 'description': 'Indicated in numbers'}, 'ROW': {'value': None, 'description': 'Indicated in numbers'}},
        'MEDIA': {'value': None, 'description': 'File path containing the media description'},
        'BACTERIA': [{'SPECIES': None, 'STRAIN': None},{'SPECIES': None, 'STRAIN': None}],
        'BLANK': {'value': None, 'description': 'Boolean. True if the experiment is blank. False otherwise.'},
        'INOCULUM_CONCENTRATION': {'value': None, 'description': 'Indicated in XXX'},
        'INOCULUM_VOLUME': {'value': None, 'description': 'Indicate in mL'},
        'INITIAL_PH': None,
        'INITIAL_TEMPERATURE': {'value': None, 'description': 'Indicated in Celsius'},
        'CARBON_SOURCE': {'value': None, 'description': 'Boolean. True if the carbon source present. False otherwise.'},
        'ANTIBIOTIC': {'value': None, 'description': 'Boolean. True if antibiotic present. False otherwise.'},
        'DESCRIPTION': {'value': None, 'description': 'Description of the experiment'},
        'FILES': {'value': None, 'description': 'Directory with the files corresponding to this experiment.'}
        }

    if num_experiments > 0: final_dict['EXPERIMENT'] = []
    for i in range(num_experiments):
        # exp_dict['EXPERIMENT_NUMBER'] = i+1
        final_dict['EXPERIMENT'].append(exp_dict)
    
    return final_dict

def addPerturbationYml(final_dict, num_perturbations):
    pert_dict = {
        # 'PERTURBATION_NUMBER': 0,
        'PROPERTY': {'value': None, 'description': 'Indicate which property has been perturbed'},
        'NEW_VALUE': {'value': None, 'description': 'New value of the perturbed property'},
        'STARTING_TIME': {'value': None, 'description': 'Time in minutes'},
        'ENDING_TIME': {'value': None, 'description': 'Time in minutes'},
        'DESCRIPTION': {'value': None, 'description': 'Description of the perturbation'},
        'FILES': {'value': None, 'description': 'Directory with the files corresponding to this perturbation.'}
        }
    
    if num_perturbations > 0: final_dict['PERTURBATION'] = []
    for i in range(num_perturbations):
        # pert_dict['PERTURBATION_NUMBER'] = i+1
        final_dict['PERTURBATION'].append(pert_dict)
    
    return final_dict

def getExperimentInfo(file):
    with open(file, 'r') as f:
        info = yaml.safe_load(f)

        experiment = {
            'experimentName': info['experiment']['name'],
            'experimentDate': info['experiment']['date'],
            'experimentAuthor': info['experiment']['author'],
            'experimentDescription': info['experiment']['description']
        }
        
        experiment_filtered = {k: v for k, v in experiment.items() if v is not None}
        return experiment_filtered
    
def getCultivationInfo(file):
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
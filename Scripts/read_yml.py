import yaml

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
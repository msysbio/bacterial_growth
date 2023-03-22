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
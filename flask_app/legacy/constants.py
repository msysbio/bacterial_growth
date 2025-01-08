import os

# This directory MUST BE the one where the core is in the server
root_folder = os.path.abspath(os.path.dirname(__file__) + '/../../')

# This directory MUST BE the one where the core is in the server
PROJECT_DIRECTORY         = os.path.join(root_folder, "")
LOCAL_DIRECTORY           = os.path.join(root_folder, "")
LOCAL_DIRECTORY_APP       = os.path.join(LOCAL_DIRECTORY, "flask_app")
LOCAL_DIRECTORY_TEMPLATES = os.path.join(LOCAL_DIRECTORY_APP, "templates")
LOCAL_DIRECTORY_YAML      = os.path.join(LOCAL_DIRECTORY_TEMPLATES, "yaml")


class GrowthTechniques:
    def __init__(self):
        self.od        = "Optical Density"
        self.plates    = "Plate Counts"
        self.plates_ps = "Plate Counts (per species)"
        self.fc        = "Flow Cytometry"
        self.fc_ps     = "Flow Cytometry (per species)"
        self.rna       = "16S rRNA-seq"


class Vessels:
    def __init__(self):
        # 'Bottles', 'Agar-plates', 'Well-plates', 'mini-bioreactors'
        self.bottles     = "Bottles"
        self.agar_plates = "Agar plates"
        self.well_plates = "Well plates"
        self.mini_react  = "mini bioreactors"

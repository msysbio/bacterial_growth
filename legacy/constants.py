import os


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

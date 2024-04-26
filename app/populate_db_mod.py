import os
import pandas as pd
from import_into_database.yml_functions import read_yml
import db_functions as db
import yaml
import uuid
import numpy as np
from constants import *
from utils import findOccurrences, transformStringIntoList
from import_into_database.bash_functions import clusterHeaders, getFiles
from parse_raw_data import get_techniques_metabolites 
from parse_raw_data import get_measures_growth
from parse_raw_data import get_measures_abundances
import pandas as pd
import itertools

yaml.Dumper.ignore_aliases = lambda self, data: True


template_filename = LOCAL_DIRECTORY + 'template_raw_data_ex.xlsx'
list_growth = ['Optical Density (OD)','16S rRNA-seq']
list_metabolites = ['glucose']
errors = get_techniques_metabolites(list_growth, list_metabolites, template_filename)
print(errors)

if not errors:

    measures, metabos = get_measures_growth(template_filename)
    print(measures)
    print(metabos)
    abundances_per_replicate = get_measures_abundances(template_filename)
    print(abundances_per_replicate)


    LOCAL_DIRECTORY = 'C:/Users/sofia/Desktop/local_thesis_files/'

    info_file = LOCAL_DIRECTORY + 'submission_yaml.yaml'
    info = read_yml(info_file)

    info_compart_file = LOCAL_DIRECTORY + 'submission_yaml_compart.yaml'
    info_compart = read_yml(info_compart_file)

    info_pertu_file = LOCAL_DIRECTORY + 'submission_yaml_pertu.yaml'
    info_pertu = read_yml(info_pertu_file)

    info_mem_file = LOCAL_DIRECTORY + 'submission_yaml_mem.yaml'
    info_mem = read_yml(info_mem_file)

    info_comu_file = LOCAL_DIRECTORY + 'submission_yaml_comu.yaml'
    info_comu = read_yml(info_comu_file)


    def generate_unique_id():
        return str(uuid.uuid4())


    def stripping_method(celd):
        if ',' in celd:
            samples = [sample.strip() for sample in celd.split(',')]
            return samples
        else:
            return [celd.strip()]

    study_name_list = info['Study_Name']
    num_items = len(study_name_list)
    num_compart = len(info_compart['Compartment_ID'])
    num_pertu = len(info_pertu['Perturbation_ID'])
    num_mem = len(info_mem['Member_ID'])
    num_comu = len(info_comu['Comunity_ID'])


    if 'Study_Name' in info:
        study = {
            'studyName': info['Study_Name'][0],
            'studyDescription': info['Study_Description'][0],
            'studyURL': info['Study_PublicationURL'][0], #new
            'studyUniqueID': info['Study_UniqueID'][0]
            }
        if np.isnan(study['studyUniqueID']) :
            study['studyUniqueID'] = generate_unique_id()

        study_filtered = {k: v for k, v in study.items() if v is not None}
        #print(study_filtered)
        if len(study_filtered)>0:
                study_id = db.addRecord('Study', study_filtered)
                print('\nSTUDY ID: ', study_id)
        else:
            print('You must introduce some study information')
            exit()

    biorep_id_list = []
    rep_id_list = []
    compartments_id_list = []
    bio_pertu_id_list = []
    mem_id_list =[]
    comu_id_list =[]

    def search_id(search_value, data_list):
        # Using a for loop to iterate over the list of tuples
        for key, value in data_list:
            if key == search_value:
                return value  # Return the value if the key is found
        return None

    if 'Member_ID' in info_mem:
        for i in range(num_mem):
            mem_id = info_mem['Member_ID'][i]
            members = {
                'genus' : info_mem['Genus'][i],
                'species': info_mem['Species'][i],
                'NCBISpeciesId': info_mem['NCBISpeciesID'][i],
                'strain': info_mem['Strain'][i],
                'NCBIStrainId': info_mem['NCBIStrainID'][i]
                }
            members_filtered = {k: v for k, v in members.items() if v is not None}
            if len(members_filtered)>0:
                members_id = db.addRecord('Strains', members_filtered)
                mem_id_list.append((mem_id,members_id))
                print('\n MEMBER UNIQUE ID: ', members_id)
            else:
                print('You must introduce some study information')
                exit()

    if 'Compartment_ID' in info_compart:
        for i in range(num_compart):
            compartments = {
                'compartmentId' : info_compart['Compartment_ID'][i],
                'volume' : info_compart['Compartment_Volume'][i],
                'pressure': info_compart['Compartment_Pressure'][i],
                'stirring_speed': info_compart['Compartment_StirringSpeed'][i],
                'stirring_mode': info_compart['Compartment_StirringMode'][i],
                'O2': info_compart['O2%'][i],
                'CO2': info_compart['CO2%'][i],
                'H2': info_compart['H2%'][i],
                'N2': info_compart['N2%'][i],
                'inoculumConcentration': info_compart['Inoculum_Concentration'][i],
                'inoculumVolume': info_compart['Inoculum_Volume'][i],
                'initialPh': info_compart['Initial_pH'][i],
                'initialTemperature': info_compart['Initial_Temperature'][i],
                'carbonSource': info_compart['Carbon_Sourced'][i],
                'mediaName': info_compart['Media_Name'][i],
                'mediaLink': info_compart['Media_Link'][i]
                }
            compartments_filtered = {k: v for k, v in compartments.items() if v is not None}
            if len(compartments_filtered)>0:
                compartments_id = db.addRecord('Compartments', compartments_filtered)
                compartments_id_list.append((info_compart['Compartment_ID'][i], compartments_id))
                print('\n COMPARTMENTS UNIQUE ID: ', compartments_id)
            else:
                print('You must introduce some study information')
                exit()

    if 'Event_ID' in info:
        for i in range(num_items):
            biologicalreplicates = {
                'EventId': info['Event_ID'][i],
                'studyId': study_id,
                'blank':info['Blank'][i],
                'EventDescription':info['Event_Description'][i]    
            }
            biologicalreplicates_filtered = {k: v for k, v in biologicalreplicates.items() if v is not None}
            if len(biologicalreplicates_filtered)>0:
                biologicalReplicate_id = db.addRecord('Events', biologicalreplicates_filtered)
                biorep_id_list.append((info['Event_ID'][i],biologicalReplicate_id))
                print('\nEVENT ID: ', biologicalReplicate_id)
            else:
                print('You must introduce some study information')
                exit()



    if 'Perturbation_ID' in info_pertu:
        for i in range(num_pertu):
            biological_id_spec =  search_id(info_pertu['BiologicalReplicate_ID'][i],biorep_id_list)
            perturbations = {
                'perturbationId': info_pertu['Perturbation_ID'][i],
                'bioreplicateUniqueId': biological_id_spec,
                'bioreplicateId': info_pertu['BiologicalReplicate_ID'][i],
                'OLDCompartmentId': info_pertu['OLD_Compartment_ID'][i],
                'OLDComunityId': info_pertu['OLD_Comunity_ID'][i],
                'NEWCompartmentId': info_pertu['NEW_Compartment_ID'][i],
                'NEWComunityId': info_pertu['NEW_Comunity_ID'][i],
                'perturbationDescription': info_pertu['Perturbation_Description'][i],
                'perturbationMinimumValue': info_pertu['Perturbation_MinimumValue'][i],
                'perturbationMaximumValue': info_pertu['Perturbation_MaximumValue'][i],
                'perturbationStartTime': info_pertu['Perturbation_StartTime'][i],
                'perturbationEndTime': info_pertu['Perturbation_EndTime'][i],
                'perturbationFilesDirectory': info_pertu['Perturbation_FilesDirectory'][i],
                }
            perturbation_filtered = {k: v for k, v in perturbations.items() if v is not None}
            if len(perturbation_filtered)>0:
                perturbation_id=db.addRecord('Perturbation', perturbation_filtered)
                print('\nPERTURBATION UNIQUE ID: ', perturbation_id)
            else:
                print('No perturbations reported')

    if 'Comunity_ID' in info_comu:
        for i in range(num_comu):
            strain_id = search_id(info_comu['Member_ID'][i],mem_id_list)
            comunities = {
                'comunityId': info_comu['Comunity_ID'][i],
                'strainId': strain_id
            }
            comunities_filtered = {k: v for k, v in comunities.items() if v is not None}
            if len(comunities_filtered)>0:
                comunities_id = db.addRecord('Comunity', comunities_filtered)
                comu_id_list.append((info_comu['Comunity_ID'][i],comunities_id))
                print('\nCOMUNITY UNIQUE ID: ', comunities_id)
            else:
                print('You must introduce some study information')
                exit()


    if 'Event_ID' in info:
        for i in range(num_items):
            comp_biorep = stripping_method(info['Compartment_ID'][i])
            comu_biorep = stripping_method(info['Comunity_ID'][i])
            for j,k in zip(comp_biorep, itertools.cycle(comu_biorep)):
                comp_per_biorep={
                    'EventUniqueId': search_id(info['Event_ID'][i],biorep_id_list),
                    'EventId': info['Event_ID'][i],
                    'compartmentUniqueId': search_id(j, compartments_id_list),
                    'compartmentId': j,
                    'comunityUniqueId': search_id(k,comu_id_list),
                    'comunityId': k
                }
                if len(comp_per_biorep)>0:
                    db.addRecord('CompartmentsPerEvent', comp_per_biorep)
                    print('\CompartmentsPerEvent Populated')
            tech_biorep = stripping_method(info['Growth_Technique'][i])
            unit_biorep = stripping_method(info['Growth_Units'][i])
            for j, k in zip(tech_biorep, unit_biorep):
                tech_per_biorep={
                    'EventUniqueId': search_id(info['Event_ID'][i],biorep_id_list),
                    'EventId': info['Event_ID'][i],
                    'technique': j,
                    'techniqueUnit': k
                }
                if len(tech_per_biorep)>0:
                    db.addRecord('TechniquesPerEvent', tech_per_biorep)
                    print('\TechniquesPerEvent Populated')
            rep_biorep = stripping_method(info['BiologicalReplicate_IDs'][i])
            plate_number = stripping_method(str(info['Plate_Number'][i]))
            position = stripping_method(info['Plate_Position'][i])
            for j, k, h in zip(rep_biorep,plate_number,position):
                list_measures = measures[j]
                od = 0
                od_std = 0
                fc = 0
                fc_std = 0
                platecounts = 0
                platecounts_std = 0
                ph = 0 
                if 'OD' in list_measures:
                    od = 1
                if 'OD_std' in list_measures:
                    od_std = 1
                if 'FC' in list_measures:
                    fc = 1
                if 'FC_std' in list_measures:
                    fc_std = 1
                if 'Plate_counts' in list_measures:
                    platecounts = 1
                if 'Plate_counts_std' in list_measures:
                    platecounts_std = 1
                if 'pH' in list_measures:
                    ph = 1
                rep_per_biorep = {
                    'EventUniqueId': search_id(info['Event_ID'][i],biorep_id_list),
                    'EventId': info['Event_ID'][i],
                    'bioreplicateId': j,
                    'plateNumber': k,
                    'platePosition': h,
                    'OD': od,
                    'OD_std': od_std, 
                    'FC': fc, 
                    'FC_std': fc_std,
                    'Plate_counts': platecounts,
                    'Plate_counts_std': platecounts_std,
                    'pH': ph,
                }
                if len(rep_per_biorep)>0:
                    rep_id = db.addRecord('BioReplicatesPerEvent', rep_per_biorep)
                    rep_id_list.append((j,rep_id))
                    print('\BioReplicatesPerEvent Populated')
            
            for j in rep_biorep:
                list_metabo = metabos[j]
                list_abundances = abundances_per_replicate[j]
                for k in list_metabo:
                    cheb_id = db.getChebiId(k)
                    metabo_rep = {
                        'EventUniqueId': search_id(info['Event_ID'][i],biorep_id_list),
                        'EventId': info['Event_ID'][i],
                        'bioreplicateId': j,
                        'bioreplicateUniqueId' : search_id(j,rep_id_list) ,
                        'metabo_name' : k,
                        'cheb_id': cheb_id
                    }
                    if len(metabo_rep)>0:
                        db.addRecord('MetabolitePerEvent', metabo_rep)
                        print('\MetabolitePerReplicates Populated')

                for h in list_abundances:
                    abundance ={
                        'EventUniqueId': search_id(info['Event_ID'][i],biorep_id_list),
                        'EventId': info['Event_ID'][i],
                        'bioreplicateId': j,
                        'bioreplicateUniqueId' : search_id(j,rep_id_list) ,
                        'strainId': search_id(h,mem_id_list),
                        'memberId': h
                    }
                    if len(abundance)>0:
                        db.addRecord('Abundances', abundance)
                        print('\Abundances Populated')



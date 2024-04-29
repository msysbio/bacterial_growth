import os
import math
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
from datetime import datetime

yaml.Dumper.ignore_aliases = lambda self, data: True

def populate_db(list_growth, list_metabolites, template_filename,info_file_study,info_file_experiments,info_compart_file,info_mem_file,info_pert_file):
    template_filename = LOCAL_DIRECTORY + 'template_raw_data_ex2.xlsx'
    list_growth = ['Optical Density (OD)','16S rRNA-seq']
    list_metabolites = ['glucose']
    errors = get_techniques_metabolites(list_growth, list_metabolites, template_filename)
    print(errors)
    erros_logic = []
    if not errors:

        measures, metabos = get_measures_growth(template_filename)
        print(measures)
        print(metabos)
        abundances_per_replicate = get_measures_abundances(template_filename)
        print(abundances_per_replicate)


        LOCAL_DIRECTORY = 'C:/Users/sofia/Desktop/local_thesis_files/'
        info_file_study = LOCAL_DIRECTORY + 'STUDY.yaml'
        info_file_experiments = LOCAL_DIRECTORY + 'EXPERIMENTS.yaml'
        info_compart_file = LOCAL_DIRECTORY + 'COMPARTMENTS.yaml'
        info_mem_file = LOCAL_DIRECTORY + 'COMMUNITY_MEMBERS.yaml'
        info_comu_file = LOCAL_DIRECTORY + 'COMMUNITIES.yaml'
        info_pert_file = LOCAL_DIRECTORY + 'PERTURBATIONS.yaml'

        info_study = read_yml(info_file_study)
        info = read_yml(info_file_experiments)
        info_compart = read_yml(info_compart_file)
        info_pertu = read_yml(info_pert_file)
        info_mem = read_yml(info_mem_file)
        info_comu = read_yml(info_comu_file)


        def generate_unique_id():
            return str(uuid.uuid4())


        def stripping_method(celd):
            if ',' in celd:
                samples = [sample.strip() for sample in celd.split(',')]
                return samples
            else:
                return [celd.strip()]

        study_name_list = info_study['Study_Name']
        num_items_study = len(study_name_list)
        experiment_name_list = info['Experiment_ID']
        num_experiment = len(experiment_name_list)
        num_compart = len(info_compart['Compartment_ID'])
        num_pertu = len(info_pertu['Perturbation_ID'])
        num_mem = len(info_mem['Member_ID'])
        num_comu = len(info_comu['Community_ID'])


        if 'Study_Name' in info_study:
            study = {
                'studyName': info_study['Study_Name'][0],
                'studyDescription': info_study['Study_Description'][0],
                'studyURL': info_study['Study_PublicationURL'][0],
                'studyUniqueID': info_study['Study_UniqueID'][0],
                'projectUniqueID':  info_study['Project_UniqueID'][0]
                }
            if np.isnan(study['studyUniqueID']) :
                study['studyUniqueID'] = generate_unique_id()

            if np.isnan(study['projectUniqueID']) :
                study['projectUniqueID'] = generate_unique_id()

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
                    'studyId': study_id,
                    'memberId' : info_mem['Member_ID'][i],
                    'defined': info_mem['Defined'][i],
                    'memberName': info_mem['Member_Name'][i],
                    'NCBId': info_mem['NCBI_ID'][i],
                    'descriptionMember': info_mem['Description'][i]
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
                    'studyId': study_id,
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
                    'carbonSource': info_compart['Carbon_Source'][i],
                    'mediaName': info_compart['Medium_Name'][i],
                    'mediaLink': info_compart['Medium_Link'][i]
                    }
                compartments_filtered = {k: v for k, v in compartments.items() if v is not None}
                if len(compartments_filtered)>0:
                    compartments_id = db.addRecord('Compartments', compartments_filtered)
                    compartments_id_list.append((info_compart['Compartment_ID'][i], compartments_id))
                    print('\n COMPARTMENTS UNIQUE ID: ', compartments_id)
                else:
                    print('You must introduce some study information')
                    exit()

        if 'Experiment_ID' in info:
            for i in range(num_experiment):
                biologicalreplicates = {
                    'experimentId': info['Experiment_ID'][i],
                    'studyId': study_id,
                    'experimentDescription': info['Experiment_Description'][i],  
                    'cultivationMode': info['Cultivation_Mode'][i],
                    'controlDescription': info['Control_Description'][i]
                }
                biologicalreplicates_filtered = {k: v for k, v in biologicalreplicates.items() if v is not None}
                if len(biologicalreplicates_filtered)>0:
                    biologicalReplicate_id = db.addRecord('Experiments', biologicalreplicates_filtered)
                    biorep_id_list.append((info['Experiment_ID'][i],biologicalReplicate_id))
                    print('\nEXPERIMENT ID: ', biologicalReplicate_id)
                else:
                    print('You must introduce some study information')
                    exit()

        if 'Community_ID' in info_comu:
            for i in range(num_comu):
                member = stripping_method(info_comu['Member_ID'][i])
                for j in member:
                    strain_id = search_id(j,mem_id_list)
                    if strain_id == None:
                        error_ms  = 'Member_ID in COMMUNITIES sheet is not defined in COMMUNITY_MEMBERS. Please check!'
                        erros_logic.append(error_ms)
                        return erros_logic
                    comunities = {
                        'studyId': study_id,
                        'comunityId': info_comu['Community_ID'][i],
                        'strainId': strain_id
                    }
                    comunities_filtered = {k: v for k, v in comunities.items() if v is not None}
                    if len(comunities_filtered)>0:
                        comunities_id = db.addRecord('Comunity', comunities_filtered)
                        comu_id_list.append((info_comu['Community_ID'][i],comunities_id))
                        print('\nCOMUNITY UNIQUE ID: ', comunities_id)
                    else:
                        print('You must introduce some study information')
                        exit()

        if 'Perturbation_ID' in info_pertu:
            for i in range(num_pertu):
                biological_id_spec =  search_id(info_pertu['Experiment_ID'][i],biorep_id_list)
                if biological_id_spec == None:
                    error_ms  = f"Experiment_ID {info_pertu['Experiment_ID'][i]} in PERTURBATIONS sheet is not defined in EXPERIMENTS. Please check!"
                    erros_logic.append(error_ms)
                    return erros_logic
                if not isinstance(info_pertu['OLD_Compartment_ID'][i], float)  and  (info_pertu['OLD_Compartment_ID'][i] not in info_compart['Compartment_ID']):
                    error_ms = f"OLD_Compartment_ID {info_pertu['OLD_Compartment_ID'][i]} in PERTURBATIONS sheet is not defined in COMPARTMENTS. Please check!"
                    erros_logic.append(error_ms)
                    return erros_logic
                if not isinstance(info_pertu['NEW_Compartment_ID'][i], float) and (info_pertu['NEW_Compartment_ID'][i] not in info_compart['Compartment_ID']):
                    error_ms = f"NEW_Compartment_ID {info_pertu['NEW_Compartment_ID'][i]} in PERTURBATIONS sheet is not defined in COMPARTMENTS. Please check!"
                    erros_logic.append(error_ms)
                    return erros_logic
                print(type(info_pertu['OLD_Community_ID'][i]))
                if not isinstance(info_pertu['OLD_Community_ID'][i], float) and info_pertu['OLD_Community_ID'][i] not in info_comu['Community_ID']:
                    error_ms = f"OLD_Community_ID {info_pertu['OLD_Community_ID'][i]} in PERTURBATIONS sheet is not defined in COMMUNITITES. Please check!"
                    erros_logic.append(error_ms)
                    return erros_logic
                if not isinstance(info_pertu['NEW_Community_ID'][i], float) and (info_pertu['NEW_Community_ID'][i] not in info_comu['Community_ID']):
                    error_ms = f"NEW_Community_ID {info_pertu['NEW_Community_ID'][i]} in PERTURBATIONS sheet is not defined in COMMUNITITES. Please check!"
                    erros_logic.append(error_ms)
                    return erros_logic
                perturbations = {
                    'studyId': study_id,
                    'perturbationId': info_pertu['Perturbation_ID'][i],
                    'experimentUniqueId': biological_id_spec,
                    'experimentId': info_pertu['Experiment_ID'][i],
                    'OLDCompartmentId': info_pertu['OLD_Compartment_ID'][i],
                    'OLDComunityId': info_pertu['OLD_Community_ID'][i],
                    'NEWCompartmentId': info_pertu['NEW_Compartment_ID'][i],
                    'NEWComunityId': info_pertu['NEW_Community_ID'][i],
                    'perturbationDescription': info_pertu['Perturbation_Description'][i],
                    'perturbationMinimumValue': info_pertu['Perturbation_MinimumValue'][i],
                    'perturbationMaximumValue': info_pertu['Perturbation_MaximumValue'][i],
                    'perturbationStartTime': datetime.strptime(info_pertu['Perturbation_StartTime'][i], '%H:%M:%S').time(),
                    'perturbationEndTime': datetime.strptime(info_pertu['Perturbation_EndTime'][i], '%H:%M:%S').time()
                    }
                perturbation_filtered = {k: v for k, v in perturbations.items() if v is not None}
                if len(perturbation_filtered)>0:
                    perturbation_id=db.addRecord('Perturbation', perturbation_filtered)
                    print('\nPERTURBATION UNIQUE ID: ', perturbation_id)
                else:
                    print('No perturbations reported')



        if 'Experiment_ID' in info:
            for i in range(num_experiment):
                comp_biorep = stripping_method(info['Compartment_ID'][i])
                comu_biorep = stripping_method(info['Community_ID'][i])
                for j,k in zip(comp_biorep, itertools.cycle(comu_biorep)):
                    comp_per_biorep={
                        'experimentUniqueId': search_id(info['Experiment_ID'][i],biorep_id_list),
                        'experimentId': info['Experiment_ID'][i],
                        'compartmentUniqueId': search_id(j, compartments_id_list),
                        'compartmentId': j,
                        'comunityUniqueId': search_id(k,comu_id_list),
                        'comunityId': k
                    }
                    if len(comp_per_biorep)>0:
                        db.addRecord('CompartmentsPerExperiment', comp_per_biorep)
                        print('\CompartmentsPerExperiment Populated')
                tech_biorep = stripping_method(info['Measurement_Technique'][i])
                unit_biorep = stripping_method(info['Measurement_Technique'][i])
                if len(tech_biorep) != len(unit_biorep):
                    error_ms = 'Measurement_Technique and Measurement_Technique must have the same number of entries per celd.'
                    error_ms.append(error_ms)

                for j, k in zip(tech_biorep, unit_biorep):
                    tech_per_biorep={
                        'experimentUniqueId': search_id(info['Experiment_ID'][i],biorep_id_list),
                        'experimentId': info['Experiment_ID'][i],
                        'technique': j,
                        'techniqueUnit': k
                    }
                    if len(tech_per_biorep)>0:
                        db.addRecord('TechniquesPerExperiment', tech_per_biorep)
                        print('\TechniquesPerExperiment Populated')
                rep_biorep = stripping_method(info['Biological_Replicate_IDs'][i])
                rep_controls = stripping_method(str(info['Control'][i]))
                print(rep_controls)
                for j in range(len(rep_biorep)):
                    print(rep_biorep[j])
                    list_measures = measures.get(rep_biorep[j])
                    if not list_measures:
                        error_ms = f"Biological_Replicate_ID: {rep_biorep[j]} was not defined in the raw data template excel. Please correct!"
                        erros_logic.append(error_ms)
                        return erros_logic

                    elif list_measures:
                        control = 0
                        od = 0
                        od_std = 0
                        fc = 0
                        fc_std = 0
                        platecounts = 0
                        platecounts_std = 0
                        ph = 0
                        if rep_biorep[j] in rep_controls:
                            control = 1
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
                            'experimentUniqueId': search_id(info['Experiment_ID'][i],biorep_id_list),
                            'experimentId': info['Experiment_ID'][i],
                            'bioreplicateId': rep_biorep[j],
                            'control': control,
                            'OD': od,
                            'OD_std': od_std, 
                            'FC': fc, 
                            'FC_std': fc_std,
                            'Plate_counts': platecounts,
                            'Plate_counts_std': platecounts_std,
                            'pH': ph,
                        }
                        if len(rep_per_biorep)>0:
                            rep_id = db.addRecord('BioReplicatesPerExperiment', rep_per_biorep)
                            rep_id_list.append((rep_biorep[j],rep_id))
                            print('\BioReplicatesPerExperiment Populated')
                
                for j in range(len(rep_biorep)):
                    list_metabo = metabos.get(rep_biorep[j])
                    list_abundances = abundances_per_replicate.get(rep_biorep[j])
                    if list_metabo:
                        for k in list_metabo:
                            cheb_id = db.getChebiId(k)
                            metabo_rep = {
                                'experimentUniqueId': search_id(info['Experiment_ID'][i],biorep_id_list),
                                'experimentId': info['Experiment_ID'][i],
                                'bioreplicateId': rep_biorep[j],
                                'bioreplicateUniqueId': search_id(rep_biorep[j],rep_id_list) ,
                                'metabo_name' : k,
                                'cheb_id': cheb_id
                            }
                            if len(metabo_rep)>0:
                                db.addRecord('MetabolitePerExperiment', metabo_rep)
                                print('\MetabolitePerExperiment Populated')
                    if list_abundances:
                        for h in list_abundances:
                            abundance ={
                                'experimentUniqueId': search_id(info['Experiment_ID'][i],biorep_id_list),
                                'experimentId': info['Experiment_ID'][i],
                                'bioreplicateId': rep_biorep[j],
                                'bioreplicateUniqueId' : search_id(rep_biorep[j],rep_id_list) ,
                                'strainId': search_id(h,mem_id_list),
                                'memberId': h
                            }
                            if len(abundance)>0:
                                db.addRecord('Abundances', abundance)
                                print('\Abundances Populated')
        print(erros_logic)
    return erros_logic, study['studyUniqueID'],study['projectUniqueID']


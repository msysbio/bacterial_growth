import itertools
import math
import os
import datetime

import sqlalchemy as sql

import legacy.db_functions as db
from legacy.yml_functions import read_yml
from legacy.parse_raw_data import (
    get_techniques_metabolites,
    get_measures_growth,
    get_measures_reads,
    get_measures_counts,
    get_replicate_metadata,
)

# Validate that project ids correspond between submission and spreadsheet
# Rewrite project and study creation/update to use ORM style, update from submission only


def save_measurements_to_database(conn, yml_dir, submission_form, data_template, study, project):
    submission = submission_form.submission

    list_microbial_strains = [t.tax_names for t in submission_form.fetch_taxa()]
    list_microbial_strains += [strain['name'] for strain in submission_form.fetch_new_strains()]

    info_file_study       = os.path.join(yml_dir, 'STUDY.yaml')
    info_file_experiments = os.path.join(yml_dir, 'EXPERIMENTS.yaml')
    info_compart_file     = os.path.join(yml_dir, 'COMPARTMENTS.yaml')
    info_mem_file         = os.path.join(yml_dir, 'COMMUNITY_MEMBERS.yaml')
    info_comu_file        = os.path.join(yml_dir, 'COMMUNITIES.yaml')
    info_pert_file        = os.path.join(yml_dir, 'PERTURBATIONS.yaml')

    # TODO (2025-04-03) Apply validation
    #
    # list_growth = submission.studyDesign['technique_types']
    # list_metabolites = [m.metabo_name for m in submission_form.fetch_all_metabolites()]
    #
    # checks that all the options selected by the user in the interface match the uploaded raw data template
    # errors = get_techniques_metabolites(list_growth, list_metabolites, list_microbial_strains, data_template)
    # if errors:
    #     return errors, []

    errors       = []
    errors_logic = []

    study_id     = study.studyId
    study_uuid   = submission.studyUniqueID
    project_id   = project.projectId
    project_uuid = submission.projectUniqueID

    #defining the dictioraries depending on the raw data uploaded by the user

    replicate_metadata = get_replicate_metadata(data_template)

    #reads all the yaml file
    info_study       = read_yml(info_file_study)
    info_experiments = read_yml(info_file_experiments)
    info_compart     = read_yml(info_compart_file)
    info_pertu       = read_yml(info_pert_file)
    info_mem         = read_yml(info_mem_file)
    info_comu        = read_yml(info_comu_file)

    #defining dictionaries per every yaml file
    experiment_name_list = info_experiments['Experiment_ID']

    #defining the number of rows with information in every yaml
    num_experiment   = len(experiment_name_list)
    num_compart      = len(info_compart['Compartment_ID'])
    num_pertu        = len(info_pertu['Perturbation_ID'])
    num_mem          = len(info_mem['Member_ID'])
    num_comu         = len(info_comu['Community_ID'])
    num_rep_metadata = len(replicate_metadata['Biological_Replicate_id'])

    #defining list that will save all the names and their corresponding ids
    biorep_id_list       = []
    rep_id_list          = []
    compartments_id_list = []
    mem_id_list          = []
    mem_name_id_list     = []
    comu_id_list         = []

    if submission_form.type == 'update_study':
        # Clear out previous data by studyId, in reverse insertion order:
        data_tables = [
            "Measurements",
            "BioReplicatesMetadata",
            "MetabolitePerExperiment",
            "BioReplicatesPerExperiment",
            "TechniquesPerExperiment",
            "CompartmentsPerExperiment",
            "Perturbation",
            "Community",
            "Experiments",
            "Compartments",
            "Strains",
        ]

        for table in data_tables:
            conn.execute(
                sql.text(f"DELETE FROM {table} WHERE studyId = :study_id"),
                {'study_id': study_id}
            )

        # Clear out previous data by studyUniqueID, in reverse insertion order:
        data_tables = [
            "MeasurementTechniques",
        ]
        for table in data_tables:
            conn.execute(
                sql.text(f"DELETE FROM {table} WHERE studyUniqueID = :study_uuid"),
                {'study_uuid': study_uuid}
            )

    # populating strains table
    if 'Member_ID' in info_mem:
        # TODO (2025-03-25) Look up information from the submission, by name?

        for i in range(num_mem):
            mem_id = info_mem['Member_ID'][i]
            members = {
                'studyId': study_id,
                'memberId' : info_mem['Member_ID'][i],
                'defined': info_mem['Defined'][i],
                'memberName': info_mem['Member_Name'][i],
                'NCBId': info_mem['NCBI_ID'][i],
                'assemblyGenBankId': info_mem['Assembly_GenBank_ID'][i],
                'descriptionMember': info_mem['Description'][i],
            }
            members_filtered = {k: v for k, v in members.items() if v is not None}
            if len(members_filtered)>0:
                members_id = db.addRecord(conn, 'Strains', members_filtered)
                mem_id_list.append((mem_id,members_id))
                mem_name_id_list.append((info_mem['Member_Name'][i],mem_id))
                print('\n MEMBER UNIQUE ID: ', members_id)
            else:
                print('You must introduce some study information')
                exit()

    # populating compartments table
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
                'mediaNames': info_compart['Medium_Name'][i],
                'mediaLink': info_compart['Medium_Link'][i]
                }
            compartments_filtered = {k: v for k, v in compartments.items() if v is not None}
            if len(compartments_filtered)>0:
                compartments_id = db.addRecord(conn, 'Compartments', compartments_filtered)
                compartments_id_list.append((info_compart['Compartment_ID'][i], compartments_id))
                print('\n COMPARTMENTS UNIQUE ID: ', compartments_id)
            else:
                print('You must introduce some study information')
                exit()

    # populating experiments table
    if 'Experiment_ID' in info_experiments:
        for i in range(num_experiment):
            biologicalreplicates = {
                'experimentId': info_experiments['Experiment_ID'][i],
                'studyId': study_id,
                'experimentDescription': info_experiments['Experiment_Description'][i],
                'cultivationMode': info_experiments['Cultivation_Mode'][i],
                'controlDescription': info_experiments['Control_Description'][i]
            }
            biologicalreplicates_filtered = {k: v for k, v in biologicalreplicates.items() if v is not None}
            if len(biologicalreplicates_filtered)>0:
                biologicalReplicate_id = db.addRecord(conn, 'Experiments', biologicalreplicates_filtered)
                biorep_id_list.append((info_experiments['Experiment_ID'][i],biologicalReplicate_id))
                print('\nEXPERIMENT ID: ', biologicalReplicate_id)
            else:
                print('You must introduce some study information')
                exit()

    #populating Community table
    if 'Community_ID' in info_comu:
        for i in range(num_comu):
            member = stripping_method(info_comu['Member_ID'][i])

            for j in member:
                strain_id = search_id(j,mem_id_list)
                if strain_id == None:
                    error_ms  = 'Member_ID in COMMUNITIES sheet is not defined in COMMUNITY_MEMBERS. Please check!'
                    errors_logic.append(error_ms)
                comunities = {
                    'studyId': study_id,
                    'communityId': info_comu['Community_ID'][i],
                    'strainId': strain_id
                }
                comunities_filtered = {k: v for k, v in comunities.items() if v is not None}
                if len(comunities_filtered)>0:
                    comunities_id = db.addRecord(conn, 'Community', comunities_filtered)
                    comu_id_list.append((info_comu['Community_ID'][i],comunities_id))
                    print('\nCOMUNITY UNIQUE ID: ', comunities_id)
                else:
                    print('You must introduce some study information')
                    exit()

    #populating perturbations table
    if 'Perturbation_ID' in info_pertu:
        for i in range(num_pertu):
            biological_id_spec =  search_id(info_pertu['Experiment_ID'][i],biorep_id_list)
            if biological_id_spec == None:
                error_ms  = f"Experiment_ID {info_pertu['Experiment_ID'][i]} in PERTURBATIONS sheet is not defined in EXPERIMENTS. Please check!"
                errors_logic.append(error_ms)
            if not isinstance(info_pertu['OLD_Compartment_ID'][i], float)  and  (info_pertu['OLD_Compartment_ID'][i] not in info_compart['Compartment_ID']):
                error_ms = f"OLD_Compartment_ID {info_pertu['OLD_Compartment_ID'][i]} in PERTURBATIONS sheet is not defined in COMPARTMENTS. Please check!"
                errors_logic.append(error_ms)
            if not isinstance(info_pertu['NEW_Compartment_ID'][i], float) and (info_pertu['NEW_Compartment_ID'][i] not in info_compart['Compartment_ID']):
                error_ms = f"NEW_Compartment_ID {info_pertu['NEW_Compartment_ID'][i]} in PERTURBATIONS sheet is not defined in COMPARTMENTS. Please check!"
                errors_logic.append(error_ms)
            if not isinstance(info_pertu['OLD_Community_ID'][i], float) and info_pertu['OLD_Community_ID'][i] not in info_comu['Community_ID']:
                error_ms = f"OLD_Community_ID {info_pertu['OLD_Community_ID'][i]} in PERTURBATIONS sheet is not defined in COMMUNITITES. Please check!"
                errors_logic.append(error_ms)
            if not isinstance(info_pertu['NEW_Community_ID'][i], float) and (info_pertu['NEW_Community_ID'][i] not in info_comu['Community_ID']):
                error_ms = f"NEW_Community_ID {info_pertu['NEW_Community_ID'][i]} in PERTURBATIONS sheet is not defined in COMMUNITITES. Please check!"
                errors_logic.append(error_ms)
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
                perturbation_id=db.addRecord(conn, 'Perturbation', perturbation_filtered)

    if 'Experiment_ID' in info_experiments:
        for i in range(num_experiment):
            comp_biorep = stripping_method(info_experiments['Compartment_ID'][i])
            comu_biorep = stripping_method(info_experiments['Community_ID'][i])

            # TODO Impossible to add a blank community, since there is one entry in "Community" for each member

            for j,k in zip(comp_biorep, itertools.cycle(comu_biorep)):
                community_unique_id = search_id(k, comu_id_list, allow_missing=True)
                if community_unique_id is None:
                    # This community was blank, we will currently not insert any data for it
                    continue

                comp_per_biorep={
                    'studyId': study_id,
                    'experimentUniqueId': search_id(info_experiments['Experiment_ID'][i],biorep_id_list),
                    'experimentId': info_experiments['Experiment_ID'][i],
                    'compartmentUniqueId': search_id(j, compartments_id_list),
                    'compartmentId': j,
                    'communityUniqueId': community_unique_id,
                    'communityId': k
                }
                comp_per_biorep_filtered = {t: v for t, v in comp_per_biorep.items() if v is not None}
                if len(comp_per_biorep_filtered)>0:
                    db.addRecord(conn, 'CompartmentsPerExperiment', comp_per_biorep_filtered)
            tech_biorep = stripping_method(info_experiments['Measurement_Technique'][i])
            unit_biorep = stripping_method(info_experiments['Measurement_Technique'][i])
            if len(tech_biorep) != len(unit_biorep):
                error_ms = 'Measurement_Technique and Measurement_Technique must have the same number of entries per celd.'
                error_ms.append(error_ms)

            for j, k in zip(tech_biorep, unit_biorep):
                tech_per_biorep={
                    'studyId': study_id,
                    'experimentUniqueId': search_id(info_experiments['Experiment_ID'][i],biorep_id_list),
                    'experimentId': info_experiments['Experiment_ID'][i],
                    'technique': j,
                    'techniqueUnit': k
                }
                tech_per_biorep_filtered = {k: v for k, v in tech_per_biorep.items() if v is not None}
                if len(tech_per_biorep_filtered)>0:
                    db.addRecord(conn, 'TechniquesPerExperiment', tech_per_biorep_filtered)

            biorep_names    = stripping_method(info_experiments['Biological_Replicate_IDs'][i])
            biorep_controls = stripping_method(str(info_experiments['Control_ID'][i]))

            for j in range(len(biorep_names)):
                control = 0
                if biorep_names[j] in biorep_controls:
                    control = 1

                rep_per_biorep = {
                    'studyId' : study_id,
                    'experimentUniqueId': search_id(info_experiments['Experiment_ID'][i],biorep_id_list),
                    'experimentId': info_experiments['Experiment_ID'][i],
                    'bioreplicateId': biorep_names[j],
                    'controls': control,
                }
                rep_per_biorep_filtered = {k: v for k, v in rep_per_biorep.items() if v is not None}
                if len(rep_per_biorep_filtered)>0:
                    rep_id = db.addRecord(conn, 'BioReplicatesPerExperiment', rep_per_biorep_filtered)
                    rep_id_list.append((biorep_names[j],rep_id))

            metabolites = submission_form.fetch_all_metabolites()

            # TODO (2025-04-03) This doesn't need to be per bioreplicate, not even per experiment, it's a study-level record
            for j in range(len(biorep_names)):
                for metabolite in metabolites:
                    chebi_id = metabolite.chebi_id

                    metabo_rep = {
                        'studyId': study_id,
                        'experimentUniqueId': search_id(info_experiments['Experiment_ID'][i],biorep_id_list),
                        'bioreplicateUniqueId': search_id(biorep_names[j],rep_id_list),
                        'chebi_id': chebi_id
                    }
                    metabo_rep_filtered = {k: v for k, v in metabo_rep.items() if v is not None}
                    db.addRecord(conn, 'MetabolitePerExperiment', metabo_rep_filtered)


    if 'Biological_Replicate_id' in replicate_metadata:
        for i in range(num_rep_metadata):
            biorep_metadata = {
                'studyId' : study_id,
                'bioreplicateUniqueId': search_id(replicate_metadata['Biological_Replicate_id'][i],rep_id_list),
                'bioreplicateId': replicate_metadata['Biological_Replicate_id'][i],
                'biosampleLink': replicate_metadata['Biosample_link'][i],
                'bioreplicateDescrition': replicate_metadata['Description'][i]
            }
            biorep_metadata_filtered = {k: v for k, v in biorep_metadata.items() if v is not None}
            if len(biorep_metadata_filtered)>0:
                db.addRecord(conn, 'BioReplicatesMetadata', biorep_metadata_filtered)

    for technique in submission.techniques:
        technique.studyUniqueID = study_uuid
        conn.add(technique)

    return errors, errors_logic

#function that stripst columns where more than one value is allowed
def stripping_method(cell):
    if isinstance(cell, float) and math.isnan(cell):
        return []
    elif ',' in cell:
        samples = [sample.strip() for sample in cell.split(',')]
        return samples
    else:
        return [cell.strip()]

# function that search the id given a value
def search_id(search_value, data_list, allow_missing=False):
    # Using a for loop to iterate over the list of tuples
    for key, value in data_list:
        if key == search_value:
            return value  # Return the value if the key is found

    if allow_missing:
        return None
    else:
        raise ValueError(f"Value {repr(search_value)} not found in the keys of: {str(data_list)}")

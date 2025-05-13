import io
import tempfile
import copy
import itertools
from datetime import datetime, timedelta, UTC
from db import get_session, get_transaction

import pandas as pd
import sqlalchemy as sql

from legacy.upload_validation import validate_upload
from legacy.populate_db import save_study_design_to_database
from models import (
    Bioreplicate,
    Community,
    Compartment,
    Experiment,
    ExperimentCompartment,
    Measurement,
    Perturbation,
    Project,
    ProjectUser,
    Strain,
    Study,
    StudyMetabolite,
    StudyUser,
    Taxon,
)
from lib.util import group_by_unique_name, is_non_negative_float


def persist_submission_to_database(submission_form):
    submission = submission_form.submission
    user_uuid = submission.userUniqueID
    errors = []

    if submission_form.submission.dataFile is None:
        errors.append("Data file has not been uploaded")

    if errors:
        return errors

    # TODO (2025-04-15) Simpler transaction handling

    with tempfile.TemporaryDirectory() as yml_dir:
        with get_transaction() as db_transaction:
            db_trans_session = get_session(db_transaction)

            study   = _save_study(db_trans_session, submission_form)
            project = _save_project(db_trans_session, submission_form)

            # First, clear out existing relationships
            study.measurements           = []
            study.strains                = []
            study.experimentCompartments = []
            study.compartments           = []
            study.communities            = []
            study.experiments            = []
            study.bioreplicates          = []
            study.perturbations          = []
            study.measurementTechniques  = []
            study.studyMetabolites       = []

            _save_compartments(db_trans_session, submission_form, study)
            _save_communities(db_trans_session, submission_form, study, user_uuid)
            _save_experiments(db_trans_session, submission_form, study)
            _save_measurement_techniques(db_trans_session, submission_form, study)

            db_trans_session.flush()
            _save_measurements(db_trans_session, study, submission)

            submission_form.save()
            db_trans_session.commit()

            return []


# TODO (2025-05-11) Test (separate read_data_file, operate on dfs)
#
def validate_data_file(submission_form, data_file=None):
    submission = submission_form.submission
    data_file = data_file or submission.dataFile
    errors = []

    if not data_file:
        return []

    data_xls = data_file.content
    sheets = pd.read_excel(io.BytesIO(data_xls), sheet_name=None)

    # Validate columns:
    expected_value_columns = _get_expected_column_names(submission_form)

    for sheet_name, column_set in expected_value_columns.items():
        if sheet_name in sheets:
            df = sheets[sheet_name]

            column_set = {*column_set, 'Biological Replicate', 'Compartment', 'Time'}

            for missing_column in column_set.difference(set(df.columns)):
                errors.append(f"{sheet_name}: Missing column {missing_column}")
        else:
            errors.append(f"Missing data sheet: {sheet_name}")

    # Validate row keys:
    expected_bioreplicates = {
        bioreplicate['name']
        for experiment in submission.studyDesign['experiments']
        for bioreplicate in experiment['bioreplicates']
    }
    expected_compartments = {c['name'] for c in submission.studyDesign['compartments']}

    for sheet_name in expected_value_columns.keys():
        if sheet_name not in sheets:
            continue

        df = sheets[sheet_name]

        if 'Biological Replicate' in df:
            uploaded_bioreplicates = set(df['Biological Replicate'])

            if missing_bioreplicates := expected_bioreplicates.difference(uploaded_bioreplicates):
                bioreplicate_description = ', '.join(missing_bioreplicates)
                errors.append(f"{sheet_name}: Missing biological replicate(s): {bioreplicate_description}")

            if extra_bioreplicates := uploaded_bioreplicates.difference(expected_bioreplicates):
                bioreplicate_description = ', '.join(extra_bioreplicates)
                errors.append(f"{sheet_name}: Unexpected biological replicate(s): {bioreplicate_description}")

        if 'Compartment' in df:
            uploaded_compartments = set(df['Compartment'])

            if missing_compartments := expected_compartments.difference(set(df['Compartment'])):
                compartment_description = ', '.join(missing_compartments)
                errors.append(f"{sheet_name}: Missing compartment(s): {compartment_description}")

            if extra_compartments := uploaded_compartments.difference(expected_compartments):
                compartment_description = ', '.join(extra_compartments)
                errors.append(f"{sheet_name}: Unexpected compartment(s): {compartment_description}")

    # Validate values:
    for sheet_name, df in sheets.items():
        if sheet_name not in expected_value_columns.keys():
            continue

        missing_time_rows = []
        missing_values = {}

        # Time must be present
        if 'Time' in df:
            for index, time in enumerate(df['Time']):
                if not is_non_negative_float(time, isnan_check=True):
                    missing_time_rows.append(str(index + 1))

        if missing_time_rows:
            row_description = _format_row_list_error(missing_time_rows)
            errors.append(f"{sheet_name}: Missing or invalid time values on row(s) {row_description}")

        # For the other rows, we're looking for non-negative numbers or blanks
        value_columns = expected_value_columns[sheet_name].intersection(set(df.columns))

        for column in value_columns:
            for index, value in enumerate(df[column]):
                if not is_non_negative_float(value, isnan_check=False):
                    if column not in missing_values:
                        missing_values[column] = []
                    missing_values[column].append(str(index + 1))

            if column in missing_values:
                row_description = _format_row_list_error(missing_values[column])
                errors.append(f"{sheet_name}: Invalid values in column \"{column}\" on row(s) {row_description}")

    return errors


def _save_study(db_session, submission_form):
    submission = submission_form.submission

    params = {
        'studyId':          submission_form.study_id,
        'studyName':        submission.studyDesign['study']['name'],
        'studyDescription': submission.studyDesign['study'].get('description', ''),
        'studyURL':         submission.studyDesign['study'].get('url', ''),
        'studyUniqueID':    submission.studyUniqueID,
        'projectUniqueID':  submission.projectUniqueID,
        'timeUnits':        submission.studyDesign['time_units'],
    }

    if submission_form.type != 'update_study':
        study = Study(**Study.filter_keys(params))

        study.studyId = Study.generate_public_id(db_session)
        study.publishableAt = datetime.now(UTC) + timedelta(hours=24)

        db_session.add(StudyUser(
            studyUniqueID=submission.studyUniqueID,
            userUniqueID=submission.userUniqueID,
        ))
    else:
        study = db_session.get(Study, submission.studyUniqueID)
        study.update(**Study.filter_keys(params))

    db_session.add(study)

    return study


def _save_project(db_session, submission_form):
    submission = submission_form.submission

    params = {
        'projectId':          submission_form.project_id,
        'projectName':        submission.studyDesign['project']['name'],
        'projectDescription': submission.studyDesign['project'].get('description', ''),
        'projectUniqueID':    submission.projectUniqueID,
    }

    if submission_form.type == 'new_project':
        project = Project(**Project.filter_keys(params))
        project.projectId = Project.generate_public_id(db_session)
        db_session.add(ProjectUser(
            projectUniqueID=submission.projectUniqueID,
            userUniqueID=submission.userUniqueID,
        ))
    else:
        project = db_session.get(Project, submission.projectUniqueID)
        project.update(**Project.filter_keys(params))

    db_session.add(project)

    return project


def _save_compartments(db_session, submission_form, study):
    submission = submission_form.submission
    compartments = []

    for compartment_data in submission.studyDesign['compartments']:
        compartment = Compartment(**Compartment.filter_keys(compartment_data))
        compartments.append(compartment)

    study.compartments = compartments
    db_session.add_all(compartments)

    return compartments


def _save_communities(db_session, submission_form, study, user_uuid):
    submission = submission_form.submission
    communities = []

    for community_data in submission.studyDesign['communities']:
        community_data = copy.deepcopy(community_data)
        strain_identifiers = community_data.pop('strainIdentifiers')

        community = Community(**Community.filter_keys(community_data))
        community.strainIds = []

        for identifier in strain_identifiers:
            strain = Strain(
                study=study,
                userUniqueID=user_uuid,
            )

            if identifier.startswith('existing|'):
                taxon_id = identifier.removeprefix('existing|')
                taxon = db_session.get_one(Taxon, taxon_id)

                strain.name    = taxon.name
                strain.NCBId   = taxon.id
                strain.defined = True

            elif identifier.startswith('custom|'):
                identifier = identifier.removeprefix('custom|')
                custom_strain_data = _find_new_strain(submission, identifier)

                strain.name        = custom_strain_data['name']
                strain.description = custom_strain_data['description']
                strain.NCBId       = custom_strain_data['species']
                strain.defined     = False
            else:
                raise ValueError(f"Strain identifier {repr(identifier)} has an unexpected prefix")

            db_session.add(strain)
            db_session.flush()

            community.strainIds.append(strain.id)

        communities.append(community)

    study.communities = communities
    db_session.add_all(communities)

    return communities


def _save_experiments(db_session, submission_form, study):
    submission = submission_form.submission
    experiments = []

    communities_by_name  = group_by_unique_name(study.communities)
    compartments_by_name = group_by_unique_name(study.compartments)

    for experiment_data in submission.studyDesign['experiments']:
        experiment_data = copy.deepcopy(experiment_data)

        community_name    = experiment_data.pop('communityName')
        compartment_names = experiment_data.pop('compartmentNames')
        bioreplicates     = experiment_data.pop('bioreplicates')
        perturbations     = experiment_data.pop('perturbations')

        experiment = Experiment(
            **Experiment.filter_keys(experiment_data),
            community=communities_by_name[community_name],
        )
        db_session.add(experiment)

        for compartment_name in compartment_names:
            experiment_compartment = ExperimentCompartment(
                study=study,
                experiment=experiment,
                compartment=compartments_by_name[compartment_name],
            )
            db_session.add(experiment_compartment)

        for bioreplicate_data in bioreplicates:
            bioreplicate = Bioreplicate(
                **Bioreplicate.filter_keys(bioreplicate_data),
                study=study,
                experiment=experiment,
            )

            db_session.add(bioreplicate)

        for perturbation_data in perturbations:
            perturbation_data = copy.deepcopy(perturbation_data)

            perturbation = Perturbation(
                study=study,
                experiment=experiment,
                startTimepoint=perturbation_data.pop('startTimepoint'),
                description=perturbation_data.pop('description'),
            )

            name = perturbation_data.pop('removedCompartmentName', '')
            if name != '':
                perturbation.removedCompartmentId = compartments_by_name[name].id

            name = perturbation_data.pop('addedCompartmentName', '')
            if name != '':
                perturbation.addedCompartmentId = compartments_by_name[name].id

            name = perturbation_data.pop('oldCommunityName', '')
            if name != '':
                perturbation.oldCommunityId = communities_by_name[name].id

            name = perturbation_data.pop('newCommunityName', '')
            if name != '':
                perturbation.newCommunityId = communities_by_name[name].id

            db_session.add(perturbation)

        experiments.append(experiment)

    study.experiments = experiments
    db_session.add_all(experiments)

    return experiments


def _save_measurement_techniques(db_session, submission_form, study):
    submission = submission_form.submission
    techniques = []

    for technique in submission.build_techniques():
        technique.study = study

        if technique.metaboliteIds:
            for chebiId in technique.metaboliteIds:
                db_session.add(StudyMetabolite(
                    chebi_id=chebiId,
                    study=study,
                ))
        techniques.append(technique)

    db_session.add_all(techniques)
    return techniques


def _save_measurements(db_session, study, submission):
    data_xls = submission.dataFile.content
    sheets = pd.read_excel(io.BytesIO(data_xls), sheet_name=None)

    if 'Growth data per community' in sheets:
        df = sheets['Growth data per community']
        Measurement.insert_from_csv_string(db_session, study, df.to_csv(index=False), subject_type='bioreplicate')

    if 'Growth data per strain' in sheets:
        df = sheets['Growth data per strain']
        Measurement.insert_from_csv_string(db_session, study, df.to_csv(index=False), subject_type='strain')

    if 'Growth data per metabolite' in sheets:
        df = sheets['Growth data per metabolite']
        Measurement.insert_from_csv_string(db_session, study, df.to_csv(index=False), subject_type='metabolite')


def _find_new_strain(submission, identifier):
    for new_strain_data in submission.studyDesign['new_strains']:
        if new_strain_data['name'] == identifier:
            return new_strain_data
    else:
        raise IndexError(f"New strain with name {repr(identifier)} not found in submission")


def _get_expected_column_names(submission_form):
    submission = submission_form.submission

    community_columns  = set()
    strain_columns     = set()
    metabolite_columns = set()

    # Validate column presence:
    for technique in submission.build_techniques():
        if technique.subjectType == 'bioreplicate':
            column = technique.csv_column_name()
            community_columns.add(column)
            if technique.includeStd:
                community_columns.add(f"{column} STD")

        elif technique.subjectType == 'strain':
            for taxon in submission_form.fetch_taxa():
                column = technique.csv_column_name(taxon.name)
                strain_columns.add(column)
                if technique.includeStd:
                    strain_columns.add(f"{column} STD")

            for strain in submission.studyDesign['new_strains']:
                column = technique.csv_column_name(strain['name'])
                strain_columns.add(column)
                if technique.includeStd:
                    strain_columns.add(f"{column} STD")

        elif technique.subjectType == 'metabolite':
            for metabolite in submission_form.fetch_all_metabolites():
                column = technique.csv_column_name(metabolite.name)
                metabolite_columns.add(column)
                if technique.includeStd:
                    metabolite_columns.add(f"{column} STD")

        else:
            raise ValueError(f"Unexpected technique subjectType: {technique.subjectType}")

    return {
        'Growth data per community':  community_columns,
        'Growth data per strain':     strain_columns,
        'Growth data per metabolite': metabolite_columns,
    }


def _format_row_list_error(row_list):
    description = ', '.join(row_list[0:3])
    if len(row_list) > 3:
        description += f", and {len(row_list) - 3} more"

    return description

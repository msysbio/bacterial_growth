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
from lib.util import group_by_unique_name


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
        study = Study(**params)

        study.studyId = Study.generate_public_id(db_session)
        study.publishableAt = datetime.now(UTC) + timedelta(hours=24)

        db_session.add(StudyUser(
            studyUniqueID=submission.studyUniqueID,
            userUniqueID=submission.userUniqueID,
        ))
    else:
        study = db_session.get(Study, submission.studyUniqueID)
        study.update(**params)

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
        project = Project(**params)
        project.projectId = Project.generate_public_id(db_session)
        db_session.add(ProjectUser(
            projectUniqueID=submission.projectUniqueID,
            userUniqueID=submission.userUniqueID,
        ))
    else:
        project = db_session.get(Project, submission.projectUniqueID)
        project.update(**params)

    db_session.add(project)

    return project


def _save_compartments(db_session, submission_form, study):
    submission = submission_form.submission
    compartments = []

    for compartment_data in submission.studyDesign['compartments']:
        compartments.append(Compartment(**compartment_data))

    study.compartments = compartments
    db_session.add_all(compartments)

    return compartments


def _save_communities(db_session, submission_form, study, user_uuid):
    submission = submission_form.submission
    communities = []

    for community_data in submission.studyDesign['communities']:
        community_data = copy.deepcopy(community_data)
        strain_identifiers = community_data.pop('strainIdentifiers')

        community = Community(**community_data)
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
            **experiment_data,
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
                **bioreplicate_data,
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

    for technique in submission.techniques:
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

    # TODO (2025-05-10) Validate keys

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

import io
import tempfile
import copy
from datetime import datetime, timedelta, UTC
from db import get_session, get_transaction

import pandas as pd

from legacy.upload_validation import validate_upload
from legacy.populate_db import save_study_design_to_database
from models import (
    Community,
    Compartment,
    Measurement,
    Project,
    ProjectUser,
    Strain,
    Study,
    StudyUser,
    Taxon,
)


def persist_submission_to_database(submission_form):
    submission = submission_form.submission
    user_uuid = submission.userUniqueID
    errors = []

    if submission_form.submission.dataFile is None:
        errors.append("Data file has not been uploaded")

    if submission_form.submission.studyFile is None:
        errors.append("Study file has not been uploaded")

    if errors:
        return errors

    # TODO (2025-04-15) Simpler transaction handling

    with tempfile.TemporaryDirectory() as yml_dir:
        with get_transaction() as db_transaction:
            db_trans_session = get_session(db_transaction)
            errors = validate_upload(yml_dir, submission)

            if errors:
                return errors

            study   = _save_study(db_trans_session, submission_form)
            project = _save_project(db_trans_session, submission_form)

            _save_compartments(db_trans_session, submission_form, study)
            _save_communities(db_trans_session, submission_form, study, user_uuid)

            db_trans_session.flush()

            if errors:
                return errors

            (errors, errors_logic) = save_study_design_to_database(
                db_trans_session,
                yml_dir,
                submission_form,
                submission.dataFile.content,
                study,
                project,
            )

            if errors or errors_logic:
                return [*errors, *errors_logic]

            _save_chart_data_to_database(db_trans_session, study, submission)
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
                studyId=study.publicId,
                userUniqueID=user_uuid,
            )

            if identifier.startswith('existing|'):
                taxon_id = identifier.removeprefix('existing|')
                taxon = db_session.get_one(Taxon, taxon_id)

                strain.memberName = taxon.name
                strain.NCBId      = taxon.id
                strain.defined    = True

            elif identifier.startswith('custom|'):
                identifier = identifier.removeprefix('custom|')
                custom_strain_data = _find_new_strain(submission, identifier)

                strain.memberName        = custom_strain_data['name']
                strain.descriptionMember = custom_strain_data['description']
                strain.NCBId             = custom_strain_data['species']
                strain.defined           = False
            else:
                raise ValueError(f"Strain identifier {repr(identifier)} has an unexpected prefix")

            db_session.add(strain)
            db_session.flush()

            community.strainIds.append(strain.id)

        communities.append(community)

    study.communities = communities
    db_session.add_all(communities)

    return communities


def _save_chart_data_to_database(db_session, study, submission):
    data_xls = submission.dataFile.content
    sheets = pd.read_excel(io.BytesIO(data_xls), sheet_name=None)

    if 'Growth data per community' in sheets:
        df = sheets['Growth data per community']
        Measurement.insert_from_bioreplicates_csv(db_session, study, df.to_csv(index=False))

    if 'Growth data per strain' in sheets:
        df = sheets['Growth data per strain']
        Measurement.insert_from_strain_csv(db_session, study, df.to_csv(index=False))

    if 'Growth data per metabolite' in sheets:
        df = sheets['Growth data per metabolite']
        Measurement.insert_from_metabolites_csv(db_session, study, df.to_csv(index=False))


def _find_new_strain(submission, identifier):
    for new_strain_data in submission.studyDesign['new_strains']:
        if new_strain_data['name'] == identifier:
            return new_strain_data
    else:
        raise IndexError(f"New strain with name {repr(identifier)} not found in submission")

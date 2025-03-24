import copy
import itertools
from uuid import uuid4
from typing import List, Tuple

import sqlalchemy as sql
from sqlalchemy.orm.attributes import flag_modified

from models import (
    Taxon,
    Metabolite,
    Project,
    Study,
    Submission,
)


class SubmissionForm:
    def __init__(self, submission_id=None, step=0, db_session=None, user_uuid=None):
        self.step       = step
        self.db_session = db_session
        self.errors     = []

        defaultStudyDesign = {
            'project': {'name': None, 'description': None},
            'study':   {'name': None, 'description': None},

            'vessel_type':     None,
            'bottle_count':    None,
            'plate_count':     None,
            'vessel_count':    None,
            'column_count':    None,
            'row_count':       None,
            'timepoint_count': None,
            'technique_types': [],
            'strains':         [],
            'new_strains':     [],
            'metabolites':     [],
        }

        # Load submission object
        self.submission = None
        if submission_id is not None:
            self.submission = self.db_session.get(Submission, submission_id)
            self.submission.studyDesign = {
                **defaultStudyDesign,
                **self.submission.studyDesign,
            }

        if self.submission is None:
            self.submission = Submission(
                projectUniqueID=None,
                studyUniqueID=None,
                userUniqueID=user_uuid,
                studyDesign=defaultStudyDesign,
            )

        # Check for an existing project/study and set the submission "type" accordingly:
        self.project_id = self._find_project_id()
        self.study_id   = self._find_study_id()
        self.type       = self._determine_project_type()

    def update_project(self, data):
        # Update IDs:
        if data['project_uuid'] == '_new':
            self.submission.projectUniqueID = str(uuid4())
        else:
            self.submission.projectUniqueID = data['project_uuid']

        if data['study_uuid'] == '_new':
            self.submission.studyUniqueID = str(uuid4())
        else:
            self.submission.studyUniqueID = data['study_uuid']

        # Update text fields:
        self.submission.studyDesign['project'] = {
            'name':        data['project_name'],
            'description': data.get('project_description', ''),
        }
        self.submission.studyDesign['study'] = {
            'name':        data['study_name'],
            'description': data.get('study_description', ''),
        }
        flag_modified(self.submission, 'studyDesign')

        # Validate uniqueness:
        self._validate_unique_names()

        # Check whether projects exist:
        self.project_id = self._find_project_id()
        self.study_id   = self._find_study_id()
        self.type       = self._determine_project_type()

    def update_strains(self, data):
        self.submission.studyDesign['strains']     = data['strains']
        self.submission.studyDesign['new_strains'] = data['new_strains']
        flag_modified(self.submission, 'studyDesign')

    def update_study_design(self, data):
        study_design = self.submission.studyDesign

        study_design['vessel_type'] = data.get('vessel_type', None)

        study_design['bottle_count'] = data['bottle_count']
        study_design['plate_count']  = data['plate_count']
        study_design['column_count'] = data['column_count']
        study_design['row_count']    = data['row_count']

        if study_design['vessel_type'] == 'bottles':
            study_design['vessel_count'] = data['bottle_count']
        elif study_design['vessel_type'] == 'plates':
            study_design['vessel_count'] = data['plate_count']

        study_design['timepoint_count'] = data['timepoint_count']
        study_design['technique_types'] = data['technique_types']
        study_design['metabolites']     = data['metabolites']

        self.submission.studyDesign = study_design
        flag_modified(self.submission, 'studyDesign')

    def fetch_taxa(self):
        strains = self.submission.studyDesign['strains']

        return self.db_session.scalars(
            sql.select(Taxon)
            .where(Taxon.tax_id.in_(strains))
        ).all()

    def fetch_new_strains(self):
        new_strains = []

        for strain in self.submission.studyDesign['new_strains']:
            if 'species_name' in strain:
                continue

            new_strains.append(copy.deepcopy(strain))

            new_strains[-1]['species_name'] = self.db_session.scalars(
                sql.select(Taxon.tax_names)
                .where(Taxon.tax_id == strain['species'])
                .limit(1)
            ).one_or_none()

        return new_strains

    def fetch_metabolites(self):
        metabolites = self.submission.studyDesign['metabolites']

        return self.db_session.scalars(
            sql.select(Metabolite)
            .where(Metabolite.chebi_id.in_(metabolites))
        ).all()

    def save(self):
        self.db_session.add(self.submission)
        self.db_session.commit()

        return self.submission.id

    def has_error(self, key):
        return key in self.errors

    def error_messages(self):
        # Flatten messages per property:
        return list(itertools.chain.from_iterable(self.errors.values()))

    def html_step_classes(self, target_step):
        if self.step < target_step:
            return 'disabled'
        elif self.step == target_step:
            return 'active'
        else:
            return ''

    def _find_project_id(self):
        if self.submission.projectUniqueID is None:
            return None

        return self.db_session.scalars(
            sql.select(Project.projectId)
            .where(Project.projectUniqueID == self.submission.projectUniqueID)
        ).one_or_none()

    def _find_study_id(self):
        if self.submission.studyUniqueID is None:
            return None

        return self.db_session.scalars(
            sql.select(Study.studyId)
            .where(Study.studyUniqueID == self.submission.studyUniqueID)
        ).one_or_none()

    def _determine_project_type(self):
        if self.project_id and self.study_id:
            return 'update_study'
        elif self.project_id:
            return 'new_study'
        else:
            return 'new_project'

    def _validate_unique_names(self):
        self.errors = {}

        project_name = self.submission.studyDesign['project']['name']
        study_name   = self.submission.studyDesign['study']['name']

        if len(project_name) > 0:
            project_exists = self.db_session.query(
                sql.exists()
                .where(
                    Project.projectName == project_name,
                    Project.projectUniqueID != self.submission.projectUniqueID
                )
            ).scalar()

            if project_exists:
                self.errors['project_name'] = ["Project name is taken"]

        # TODO (2025-03-24) Discuss whether study names should be unique
        #
        # if len(study_name) > 0:
        #     study_exists = self.db_session.query(
        #         sql.exists()
        #         .where(
        #             Study.studyName == study_name,
        #             Study.studyUniqueID != self.submission.studyUniqueID
        #         )
        #     ).scalar()
        #
        #     if study_exists:
        #         self.errors['study_name'] = ["Study name is taken"]

        return len(self.errors) == 0

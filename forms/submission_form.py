from uuid import uuid4
import copy
from typing import List, Tuple

import sqlalchemy as sql

from models import (
    Taxon,
    Metabolite,
    Project,
    Study,
    Submission,
)
from db import get_session


class SubmissionForm:
    def __init__(self, data, step, db_conn=None):
        self.step       = step
        self.db_conn    = db_conn
        self.db_session = get_session(db_conn)

        # Load submission object
        if data:
            self.submission = Submission(**data)
        else:
            self.submission = Submission(
                projectUniqueID=data.get('projectUniqueID', None),
                studyUniqueID=data.get('studyUniqueID', None),
                userUniqueID=data.get('userUniqueID', 'TODO'),
                studyDesign={
                    'project':         data.get('project', {'name': None, 'description': None}),
                    'vessel_type':     data.get('vessel_type',     None),
                    'bottle_count':    data.get('bottle_count',    None),
                    'plate_count':     data.get('plate_count',     None),
                    'vessel_count':    data.get('vessel_count',    None),
                    'column_count':    data.get('column_count',    None),
                    'row_count':       data.get('row_count',       None),
                    'timepoint_count': data.get('timepoint_count', None),
                    'technique_types': data.get('technique_types', []),
                    'strains':         data.get('strains',         []),
                    'new_strains':     data.get('new_strains',     []),
                    'metabolites':     data.get('metabolites',     []),
                }
            )

        # Check for an existing project/study and set the submission "type" accordingly:
        self.project_id = self._find_project_id()
        self.study_id   = self._find_study_id()
        self.type       = self._determine_project_type()

    def update_project(self, data):
        self.type = data['submission_type']
        self.submission.studyDesign['project'] = {
            'name':        data['project_name'],
            'description': data['project_description'],
        }

        if self.type == 'new_project':
            self.submission.projectUniqueID = str(uuid4())
            self.submission.studyUniqueID   = str(uuid4())
        elif self.type == 'new_study':
            self.submission.projectUniqueID = data['project_uuid']
            self.submission.studyUniqueID   = str(uuid4())
        elif self.type == 'update_study':
            self.submission.projectUniqueID = data['project_uuid']
            self.submission.studyUniqueID   = data['study_uuid']

    def update_strains(self, data):
        self.submission.studyDesign['strains']     = data['strains']
        self.submission.studyDesign['new_strains'] = data['new_strains']

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

            new_strains[-1]['species_name'] = self.db_conn.scalars(
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

    def _asdict(self):
        return {
            'projectUniqueID': self.submission.projectUniqueID,
            'studyUniqueID':   self.submission.studyUniqueID,
            'userUniqueID':    self.submission.userUniqueID,
            'studyDesign':     self.submission.studyDesign,
        }

    def _find_project_id(self):
        if self.submission.projectUniqueID is None:
            return None

        return self.db_conn.scalars(
            sql.select(Project.projectId)
            .where(Project.projectUniqueID == self.submission.projectUniqueID)
        ).one_or_none()

    def _find_study_id(self):
        if self.submission.studyUniqueID is None:
            return None

        return self.db_conn.scalars(
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

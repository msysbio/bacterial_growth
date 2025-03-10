from uuid import uuid4
from typing import List, Tuple

import sqlalchemy as sql

from models.project import Project
from models.study import Study
from models.taxon import Taxon
from models.metabolite import Metabolite


class Submission:
    def __init__(self, data, step, db_conn=None):
        self.step    = step
        self.db_conn = db_conn

        # Step 1:
        self.type         = data.get('type',         None)
        self.project_uuid = data.get('project_uuid', None)
        self.study_uuid   = data.get('study_uuid',   None)

        self.project = data.get('project', {'name': None, 'description': None})

        # Check for an existing project/study:
        self.project_id = self._find_project_id()
        self.study_id   = self._find_study_id()

        self._sync_project_type()

        # Step 2:
        self.strains     = data.get('strains', [])
        self.new_strains = data.get('new_strains', [])

        # Step 3:
        self.vessel_type  = data.get('vessel_type', None)

        self.bottle_count = data.get('bottle_count', None)
        self.plate_count  = data.get('plate_count', None)
        self.vessel_count = data.get('vessel_count', None)
        self.column_count = data.get('column_count', None)
        self.row_count    = data.get('row_count', None)

        self.timepoint_count = data.get('timepoint_count', None)
        self.technique_types = data.get('technique_types', [])
        self.metabolites     = data.get('metabolites', [])

    def update_project(self, data):
        self.type = data['submission_type']
        self.project = {
            'name':        data['project_name'],
            'description': data['project_description'],
        }

        if self.type == 'new_project':
            self.project_uuid = str(uuid4())
            self.study_uuid   = str(uuid4())
        elif self.type == 'new_study':
            self.project_uuid = data['project_uuid']
            self.study_uuid   = str(uuid4())
        elif self.type == 'update_study':
            self.project_uuid = data['project_uuid']
            self.study_uuid   = data['study_uuid']

    def update_strains(self, data):
        self.strains     = data['strains']
        self.new_strains = data['new_strains']

    def update_study_design(self, data):
        self.vessel_type  = data.get('vessel_type', None)

        self.bottle_count = data['bottle_count']
        self.plate_count  = data['plate_count']
        self.column_count = data['column_count']
        self.row_count    = data['row_count']

        if self.vessel_type == 'bottles':
            self.vessel_count = self.bottle_count
        elif self.vessel_type == 'plates':
            self.vessel_count = self.plate_count

        self.timepoint_count = data['timepoint_count']
        self.technique_types = data['technique_types']
        self.metabolites     = data['metabolites']

    def fetch_strains(self) -> List[Tuple[str, str]]:
        return self.db_conn.execute(
            sql.select(
                Taxon.tax_id.label("id"),
                Taxon.tax_names.label("name"),
            )
            .where(Taxon.tax_id.in_(self.strains))
        ).all()

    def fetch_metabolites(self) -> List[Tuple[str, str]]:
        return self.db_conn.execute(
            sql.select(
                Metabolite.chebi_id.label("id"),
                Metabolite.metabo_name.label("name"),
            )
            .where(Metabolite.chebi_id.in_(self.metabolites))
        ).all()

    def fetch_new_strains(self):
        if len(self.new_strains) == 0:
            return []

        new_strains = sorted(self.new_strains, key=lambda s: int(s['species']))
        species_ids = [s['species'] for s in new_strains]

        query = f"""
            SELECT tax_names
            FROM Taxa
            WHERE tax_id IN ({','.join(species_ids)})
            ORDER BY tax_id
        """
        species_names = self.db_conn.execute(sql.text(query)).scalars()

        for strain, name in zip(new_strains, species_names):
            strain['species_name'] = name

        return new_strains

    def _asdict(self):
        return {
            'type':            self.type,
            'project_uuid':    self.project_uuid,
            'study_uuid':      self.study_uuid,
            'project':         self.project,
            'strains':         self.strains,
            'new_strains':     self.new_strains,
            'vessel_type':     self.vessel_type,
            'bottle_count':    self.bottle_count,
            'plate_count':     self.plate_count,
            'column_count':    self.column_count,
            'row_count':       self.row_count,
            'timepoint_count': self.timepoint_count,
            'technique_types': self.technique_types,
            'metabolites':     self.metabolites,
        }

    def _find_project_id(self):
        return self.db_conn.scalars(
            sql.select(Project.projectId)
            .where(Project.projectUniqueID == self.project_uuid)
        ).one_or_none()

    def _find_study_id(self):
        return self.db_conn.scalars(
            sql.select(Study.studyId)
            .where(Study.studyUniqueID == self.study_uuid)
        ).one_or_none()

    def _sync_project_type(self):
        if self.project_id and self.study_id:
            self.type = 'update_study'
        elif self.project_id:
            self.type = 'new_study'
        else:
            self.type = 'new_project'

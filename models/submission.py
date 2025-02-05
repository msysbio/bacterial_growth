from uuid import uuid4

import sqlalchemy as sql


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

        if self.type == 'new_project':
            self.project_uuid = str(uuid4())
            self.study_uuid = str(uuid4())

            self.project = {
                'name':        data['project_name'],
                'description': data['project_description'],
            }
        elif self.type == 'new_study':
            self.project = _get_project_data(self.db_conn, data['project_uuid'])
            if self.project:
                self.project_uuid = data['project_uuid']

            self.study_uuid = str(uuid4())
        elif self.type == 'update_study':
            self.project = _get_project_data(self.db_conn, data['project_uuid'])
            if self.project:
                self.project_uuid = data['project_uuid']

            self.study_uuid = data['study_uuid']
        else:
            raise KeyError("Unknown self type: {}".format(self.submission_type))

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

    def fetch_strains(self):
        if len(self.strains) == 0:
            return []

        # TODO (2024-09-22) Figure out a sensible way to bind ids

        query = f"""
            SELECT
                tax_id AS id,
                tax_names AS name
            FROM Taxa
            WHERE tax_id IN ({','.join(self.strains)})
        """
        result = self.db_conn.execute(sql.text(query)).all()

        return [(entry.id, entry.name) for entry in result]

    def fetch_metabolites(self):
        if len(self.metabolites) == 0:
            return []

        # TODO (2024-09-22) Figure out a sensible way to bind ids

        query = f"""
            SELECT
                chebi_id AS id,
                metabo_name AS name
            FROM Metabolites
            WHERE chebi_id IN ({','.join([f"'{chebi_id}'" for chebi_id in self.metabolites])})
        """
        result = self.db_conn.execute(sql.text(query)).all()

        return [(entry.id, entry.name) for entry in result]

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
        if self.project_uuid is None:
            return None
        query = f"SELECT projectId FROM Project WHERE projectUniqueID = :uuid"
        return self.db_conn.execute(sql.text(query), {'uuid': self.project_uuid}).scalar()

    def _find_study_id(self):
        if self.study_uuid is None:
            return None
        query = f"SELECT studyId FROM Study WHERE studyUniqueId = :uuid"
        return self.db_conn.execute(sql.text(query), {'uuid': self.study_uuid}).scalar()

    def _sync_project_type(self):
        if self.project_id and self.study_id:
            self.type = 'update_study'
        elif self.project_id:
            self.type = 'new_study'
        else:
            self.type = 'new_project'


def _get_project_data(db_conn, uuid):
    query = """
        SELECT
            projectName AS name,
            projectDescription AS description
        FROM Project
        WHERE projectUniqueID = :uuid
    """
    result = db_conn.execute(sql.text(query), {'uuid': uuid}).one_or_none()

    if result is None:
        return None
    else:
        return result._asdict()

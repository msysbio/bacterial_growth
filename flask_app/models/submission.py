from uuid import uuid4

import sqlalchemy as sql

class Submission:
    def __init__(self, data, current_step=1, db_conn=None):
        self.step = current_step
        self.db_conn = db_conn

        # Step 1:
        self.type         = data.get('type',         None)
        self.project_uuid = data.get('project_uuid', None)
        self.study_uuid   = data.get('study_uuid',   None)

        self.project = data.get('project', {'name': None, 'description': None})

        # Step 2:
        self.strains     = data.get('strains', [])
        self.new_strains = data.get('new_strains', [])

    def update_project(self, data):
        self.type = data['submission_type']

        if self.type == 'new_project':
            self.project_uuid = uuid4()
            self.study_uuid = uuid4()

            self.project = {
                'name':        data['project_name'],
                'description': data['project_description'],
            }
        elif self.type == 'new_study':
            self.project = _get_project_data(db_conn, data['project_uuid'])
            if self.project:
                self.project_uuid = data['project_uuid']

            self.study_uuid = uuid4()
        elif self.type == 'update_study':
            self.project = _get_project_data(db_conn, data['project_uuid'])
            if self.project:
                self.project_uuid = data['project_uuid']

            self.study_uuid = data['study_uuid']
        else:
            raise KeyError("Unknown self type: {}".format(submission_type))

    def update_strains(self, form):
        self.strains     = form.data['strains']
        self.new_strains = form.data['new_strains']

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
            'type':         self.type,
            'project_uuid': self.project_uuid,
            'study_uuid':   self.study_uuid,
            'project':      self.project,
            'strains':      self.strains,
            'new_strains':  self.new_strains,
        }

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

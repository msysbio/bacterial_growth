import os
import unittest
from uuid import uuid4

import sqlalchemy as sql

import db
from lib.db import get_primary_key_names

class DatabaseTest(unittest.TestCase):
    def setUp(self):
        assert os.environ['APP_ENV'] == 'test'

        self.db_session = db.get_session()

        # Clean up database state before each test:
        tables = self.db_session.execute(sql.text('SHOW TABLES')).scalars().all()
        self.db_session.execute(sql.text(f'SET FOREIGN_KEY_CHECKS = 0'))
        for table in tables:
            if table != 'MigrationVersions':
                self.db_session.execute(sql.text(f'TRUNCATE TABLE {table}'))
        self.db_session.execute(sql.text(f'SET FOREIGN_KEY_CHECKS = 1'))
        self.db_session.commit()

    def tearDown(self):
        self.db_session.close()

    def simple_query(self, query, **params):
        results = self.db_session.execute(sql.text(query), params).all()
        return [row._asdict() for row in results]

    def create_taxon(self, **params):
        self.taxa_id = getattr(self, 'taxa_id', 0) + 1
        params = {
            'tax_id': self.taxa_id,
            'tax_names': f"Taxon {self.taxa_id}",
            **params,
        }

        query = sql.text("INSERT INTO Taxa VALUES (:tax_id, :tax_names)")
        self.db_session.execute(query, params)

        return params

    def create_metabolite(self, **params):
        self.metabolite_id = getattr(self, 'metabolite_id', 0) + 1
        params = {
            'chebi_id': f"CHEBI:{self.metabolite_id}",
            'metabo_name': f"Metabolite {self.metabolite_id}",
            **params,
        }

        query = sql.text("INSERT INTO Metabolites VALUES (:chebi_id, :metabo_name)")
        self.db_session.execute(query, params)

        return params

    def create_project(self, **params):
        self.project_id = getattr(self, 'project_id', 0) + 1
        project_uuid = uuid4()

        params = {
            'projectId': project_uuid,
            'projectName': f"Project {self.project_id}",
            'projectDescription': f"Project {self.project_id}",
            'projectUniqueID': project_uuid,
            **params,
        }

        return self._create_record('Project', params)

    def create_study(self, **params):
        self.study_id = getattr(self, 'study_id', 0) + 1
        study_uuid = uuid4()

        project_uuid = self._get_or_create_dependency(params, 'projectUniqueID', 'project')

        params = {
            'studyId': f"SMGDB{self.study_id:07}",
            'projectUniqueID': project_uuid,
            'studyName': f"Study {self.study_id}",
            'studyDescription': f"Study {self.study_id}",
            'studyURL': None,
            'studyUniqueID': study_uuid,
            **params,
        }

        return self._create_record('Study', params)

    def create_experiment(self, **params):
        # TODO The experiment id *should* be `experiment_id`, but that's
        # actually the non-unique name. Some renaming needs to be done, but for
        # now, we'll call the primary key `experiment_id_key`
        self.experiment_id_key = getattr(self, 'experiment_id_key', 0) + 1

        study_id = self._get_or_create_dependency(params, 'studyId', 'study')

        params = {
            'studyId': study_id,
            'experimentId': f"Experiment {self.experiment_id_key}",
            'experimentDescription': f"Experiment {self.experiment_id_key}",
            'cultivationMode': 'chemostat',
            'controlDescription': '',
            **params,
        }

        return self._create_record('Experiments', params)

    def create_bioreplicate(self, **params):
        self.bioreplicate_uuid = str(getattr(self, 'bioreplicate_uuid', 0) + 1)

        study_id          = self._get_or_create_dependency(params, 'studyId', 'study')
        experiment_id_key = self._get_or_create_dependency(params, 'experimentUniqueId', 'experiment', studyId=study_id)

        query = "SELECT * from Study where studyId = :studyId"
        results = self.db_session.execute(sql.text(query), {'studyId': params['studyId']})

        params = {
            'studyId':              study_id,
            'bioreplicateUniqueId': self.bioreplicate_uuid,
            'bioreplicateId':       f"Bioreplicate {self.bioreplicate_uuid}",
            'experimentUniqueId':   experiment_id_key,
            'experimentId':         f"Experiment {experiment_id_key}",
            **params,
        }

        return self._create_record('BioReplicatesPerExperiment', params)

    def create_strain(self, **params):
        self.strain_id = getattr(self, 'strain_id', 0) + 1

        study_id = self._get_or_create_dependency(params, 'studyId', 'study')

        params = {
            'studyId': study_id,
            'memberId': 'Member 1',
            'defined': True,
            'memberName': 'Member 1',
            'NCBId': '1',
            'descriptionMember': 'Member 1',
            **params,
        }

        return self._create_record('Strains', params)

    def create_metabolite_per_experiment(self, **params):
        study_id          = self._get_or_create_dependency(params, 'studyId', 'study')
        experiment_uuid   = self._get_or_create_dependency(params, 'experimentUniqueId', 'experiment', studyId=study_id)
        chebi_id          = self._get_or_create_dependency(params, 'chebi_id', 'metabolite')
        bioreplicate_uuid = self._get_or_create_dependency(params, 'bioreplicateUniqueId', 'bioreplicate')

        params = {
            'studyId': study_id,
            'experimentUniqueId': experiment_uuid,
            'bioreplicateUniqueId': bioreplicate_uuid,
            'chebi_id': chebi_id,
            **params,
        }

        return self._create_record('MetabolitePerExperiment', params)

    def _create_record(self, table_name, params):
        column_list = ', '.join(params.keys())
        value_list  = ', '.join([f":{key}" for key in params])

        query = sql.text(f"INSERT INTO {table_name} ({column_list}) VALUES ({value_list})")
        result = self.db_session.execute(query, params)

        pk_names = get_primary_key_names(self.db_session, table_name)

        if len(pk_names) == 1 and pk_names[0] not in params:
            query = sql.text(f"select LAST_INSERT_ID() from {table_name}")
            result = self.db_session.execute(query).scalars().all()
            last_id = result[-1]
            params[pk_names[0]] = last_id

        return params

    def _get_or_create_dependency(self, params, key_name, object_name, **dependency_params):
        if key_name in params:
            key_value = params[key_name]
        else:
            creator_func = getattr(self, f"create_{object_name}")
            dependency_params = {
                **dependency_params,
                **params.pop(object_name, {})
            }

            object = creator_func(**dependency_params)
            key_value = object[key_name]

        return key_value


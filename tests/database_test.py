import os
import unittest
from uuid import uuid4
from decimal import Decimal

import db
from lib.db import execute_text
from models import (
    Bioreplicate,
    CalculationTechnique,
    Experiment,
    Measurement,
    MeasurementTechnique,
    Metabolite,
    Project,
    Strain,
    Study,
    StudyMetabolite,
    StudyUser,
    Submission,
    Taxon,
)


class DatabaseTest(unittest.TestCase):
    def setUp(self):
        self.assertEqual(
            os.environ.get('APP_ENV'),
            'test',
            "Make sure you `import tests.init` before anything else in the test",
        )

        self.db_conn = db.get_connection()
        self.db_session = db.get_session(conn=self.db_conn)

        # Clean up database state before each test:
        tables = execute_text(self.db_session, 'SHOW TABLES').scalars().all()
        for table in tables:
            if table != 'MigrationVersions':
                execute_text(self.db_session, f'DELETE FROM {table}')
        self.db_session.commit()

    def tearDown(self):
        self.db_session.close()

    def create_taxon(self, **params):
        self.taxa_id = getattr(self, 'taxa_id', 0) + 1
        params = {
            'tax_id':    str(self.taxa_id),
            'tax_names': f"Taxon {self.taxa_id}",
            **params,
        }

        return self._create_orm_record(Taxon, params)

    def create_metabolite(self, **params):
        self.metabolite_id = getattr(self, 'metabolite_id', 0) + 1
        params = {
            'chebi_id':    f"CHEBI:{self.metabolite_id}",
            'metabo_name': f"Metabolite {self.metabolite_id}",
            **params,
        }

        return self._create_orm_record(Metabolite, params)

    def create_project(self, **params):
        project_id = Project.generate_public_id(self.db_session)
        project_uuid = str(uuid4())

        params = {
            'projectId':       project_id,
            'projectName':     f"Project {project_id}",
            'projectUniqueID': project_uuid,
            **params,
        }

        return self._create_orm_record(Project, params)

    def create_study(self, **params):
        study_id = Study.generate_public_id(self.db_session)
        study_uuid = str(uuid4())

        project_uuid = self._get_or_create_dependency(params, 'projectUniqueID', 'project')

        params = {
            'studyId':          study_id,
            'projectUniqueID':  project_uuid,
            'studyName':        f"Study {study_id}",
            'studyUniqueID':    study_uuid,
            'timeUnits':        's',
            **params,
        }

        return self._create_orm_record(Study, params)

    def create_study_user(self, **params):
        user_uuid = str(uuid4())
        study_uuid = self._get_or_create_dependency(params, 'studyUniqueID', 'study')

        params = {
            'studyUniqueID': study_uuid,
            'userUniqueID':  user_uuid,
            **params,
        }

        return self._create_orm_record(StudyUser, params)

    def create_experiment(self, **params):
        self.experiment_sequence = getattr(self, 'experiment_sequence', 0) + 1

        study_id = self._get_or_create_dependency(params, 'studyId', 'study')

        params = {
            'studyId':      study_id,
            'experimentId': f"Experiment {self.experiment_sequence}",
            **params,
        }

        return self._create_orm_record(Experiment, params)

    def create_bioreplicate(self, **params):
        # Note: this is just a sequential number
        self.bioreplicate_uuid = getattr(self, 'bioreplicate_uuid', 0) + 1

        study_id        = self._get_or_create_dependency(params, 'studyId', 'study')
        experiment_uuid = self._get_or_create_dependency(params, 'experimentUniqueId', 'experiment', studyId=study_id)

        params = {
            'studyId':              study_id,
            'bioreplicateUniqueId': self.bioreplicate_uuid,
            'bioreplicateId':       f"Bioreplicate {self.bioreplicate_uuid}",
            'experimentUniqueId':   experiment_uuid,
            'experimentId':         f"Experiment {experiment_uuid}",
            **params,
        }

        return self._create_orm_record(Bioreplicate, params)

    def create_strain(self, **params):
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

        return self._create_orm_record(Strain, params)

    def create_study_metabolite(self, **params):
        study_id          = self._get_or_create_dependency(params, 'studyId', 'study')
        experiment_uuid   = self._get_or_create_dependency(params, 'experimentUniqueId', 'experiment', studyId=study_id)
        chebi_id          = self._get_or_create_dependency(params, 'chebi_id', 'metabolite')
        bioreplicate_uuid = self._get_or_create_dependency(params, 'bioreplicateUniqueId', 'bioreplicate')

        params = {
            'studyId':              study_id,
            'experimentUniqueId':   experiment_uuid,
            'bioreplicateUniqueId': bioreplicate_uuid,
            'chebi_id':             chebi_id,
            **params,
        }

        return self._create_orm_record(StudyMetabolite, params)

    def create_measurement(self, **params):
        study_id          = self._get_or_create_dependency(params, 'studyId', 'study')
        bioreplicate_uuid = self._get_or_create_dependency(params, 'bioreplicateUniqueId', 'bioreplicate')
        technique_id      = self._get_or_create_dependency(params, 'id', 'measurement_technique')

        subject_id   = params['subjectId']
        subject_type = params['subjectType']

        params = {
            'studyId':              study_id,
            'bioreplicateUniqueId': bioreplicate_uuid,
            'techniqueId':          technique_id,
            'position':             'A1',
            'timeInSeconds':        3600,
            'unit':                 'unknown',
            'value':                Decimal('100.000'),
            'subjectId':            subject_id,
            'subjectType':          subject_type,
            **params,
        }

        return self._create_orm_record(Measurement, params)

    def create_measurement_technique(self, **params):
        study_uuid = self._get_or_create_dependency(params, 'studyUniqueID', 'study')

        params = {
            'type': 'fc',
            'subjectType': 'bioreplicate',
            'units': '',
            'studyUniqueID': study_uuid,
            **params,
        }

        return self._create_orm_record(MeasurementTechnique, params)

    def create_submission(self, **params):
        """
        A special case of a model factory: We do not create dependencies,
        because a submission is supposed to be initialized with UUIDs that the
        Project and Study are created from.
        """
        params = {
            'studyUniqueID': str(uuid4()),
            'projectUniqueID': str(uuid4()),
            'userUniqueID': str(uuid4()),
            'studyDesign': {
                'time_units': 'h',
                'project': {
                    'name': 'Test project',
                },
                'study': {
                    'name': 'Test study',
                },
                **params.get('studyDesign', {})
            },
            **params,
        }

        return self._create_orm_record(Submission, params)

    def create_calculation_technique(self, **params):
        study_uuid = self._get_or_create_dependency(params, 'studyUniqueID', 'study')

        params = {
            'type':          'baranyi_roberts',
            'studyUniqueID': study_uuid,
            **params,
        }

        return self._create_orm_record(CalculationTechnique, params)

    def _create_orm_record(self, model_class, params):
        instance = model_class(**params)
        self.db_session.add(instance)
        self.db_session.flush()

        return instance

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
            key_value = getattr(object, key_name)

        return key_value

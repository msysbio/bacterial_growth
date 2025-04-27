import tests.init  # noqa: F401

import unittest

import sqlalchemy as sql

from lib.tasks.calculations import _update_calculation_technique
from tests.database_test import DatabaseTest

class TestCalculations(DatabaseTest):
    def test_calculation_technique_status_change(self):
        calculation_technique = self.create_calculation_technique(state='error')

        _update_calculation_technique(self.db_session, calculation_technique.id, [])
        self.assertEqual(calculation_technique.state, 'ready')

        with self.assertRaises(sql.exc.NoResultFound):
            _update_calculation_technique(self.db_session, calculation_technique.id, [{
                'bioreplicate_uuid':        'nonexistent',
                'subject_id':               'nonexistent',
                'subject_type':             'nonexistent',
                'measurement_technique_id': 'nonexistent',
            }])
        self.assertEqual(calculation_technique.state, 'error')
        self.db_session.rollback()

        _update_calculation_technique(self.db_session, calculation_technique.id, [])
        self.assertEqual(calculation_technique.state, 'ready')

        with self.assertRaises(KeyError):
            _update_calculation_technique(self.db_session, calculation_technique.id, [{
                'wrong_key': 'wrong_value',
            }])
        self.assertEqual(calculation_technique.state, 'error')

    def test_baranyi_roberts_calculation(self):
        study                 = self.create_study()
        strain                = self.create_strain(studyId=study.publicId)
        measurement_technique = self.create_measurement_technique(studyUniqueID=study.uuid)
        bioreplicate          = self.create_bioreplicate(studyId=study.publicId)
        calculation_technique = self.create_calculation_technique()

        params = {
            'bioreplicateUniqueId': bioreplicate.uuid,
            'techniqueId': measurement_technique.id,
            'subjectId': strain.id,
            'subjectType': 'strain',
        }
        self.create_measurement(**params, timeInSeconds=60,  value=10.0)
        self.create_measurement(**params, timeInSeconds=120, value=11.0)
        self.create_measurement(**params, timeInSeconds=180, value=40.0)
        self.create_measurement(**params, timeInSeconds=240, value=20.0)

        _update_calculation_technique(self.db_session, calculation_technique.id, [{
            'bioreplicate_uuid':        bioreplicate.uuid,
            'subject_id':               strain.id,
            'subject_type':             'strain',
            'measurement_technique_id': measurement_technique.id
        }])

        self.assertEqual(len(calculation_technique.calculations), 1)

        calculation = calculation_technique.calculations[0]
        self.assertEqual(len(calculation.coefficients), 4)


if __name__ == '__main__':
    unittest.main()

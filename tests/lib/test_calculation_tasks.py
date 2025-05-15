import tests.init  # noqa: F401

import unittest

import sqlalchemy as sql

from lib.calculation_tasks import _update_calculation_technique
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

        context_params = {
            'bioreplicateId': bioreplicate.id,
            'techniqueId': measurement_technique.id,
            'subjectId': strain.id,
            'subjectType': 'strain',
        }
        data = [
            (0.0,   2146.0),
            (4.0,   23640.0),
            (8.0,   400810.0),
            (12.0,  1139840.0),
            (16.0,  1418960.0),
            (20.0,  1122060.0),
            (24.0,  979120.0),
            (28.0,  874350.0),
            (32.0,  860460.0),
            (36.0,  898770.0),
            (40.0,  840550.0),
            (48.0,  964230.0),
            (60.0,  952260.0),
            (72.0,  1253140.0),
            (86.0,  1095660.0),
            (96.0,  1001220.0),
            (120.0, 967930.0),
        ]
        for (hours, value) in data:
            self.create_measurement(measurement_context=context_params, timeInSeconds=(hours * 3600), value=value)

        _update_calculation_technique(self.db_session, calculation_technique.id, [{
            'bioreplicate_uuid':        bioreplicate.id,
            'subject_id':               strain.id,
            'subject_type':             'strain',
            'measurement_technique_id': measurement_technique.id
        }])

        self.assertEqual(len(calculation_technique.calculations), 1)

        calculation = calculation_technique.calculations[0]
        self.assertEqual(len(calculation.coefficients), 4)


if __name__ == '__main__':
    unittest.main()

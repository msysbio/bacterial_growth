import tests.init  # noqa: F401

import unittest

from models import Calculation
from tests.database_test import DatabaseTest

class TestCalculation(DatabaseTest):
    def test_successful_creation(self):
        bioreplicate          = self.create_bioreplicate()
        calculation_technique = self.create_calculation_technique()
        measurement_technique = self.create_measurement_technique()
        strain                = self.create_strain()

        calculation = Calculation(
            type='baranyi_roberts',
            bioreplicateUniqueId=bioreplicate.uuid,
            calculationTechniqueId=calculation_technique.id,
            measurementTechniqueId=measurement_technique.id,
            subjectId=strain.id,
            subjectType='strain',
        )
        self.db_session.add(calculation)
        self.db_session.flush()

        self.assertIsNotNone(calculation.id)
        self.assertEqual(calculation.state, 'pending')

        with self.assertRaises(ValueError):
            calculation_technique.type = 'unexpected'
        with self.assertRaises(ValueError):
            calculation_technique.state = 'unexpected'


if __name__ == '__main__':
    unittest.main()

import tests.init  # noqa: F401

import unittest

from models import CalculationTechnique
from tests.database_test import DatabaseTest

class TestCalculationTechnique(DatabaseTest):
    def test_successful_creation(self):
        study  = self.create_study()
        strain = self.create_strain(studyId=study.publicId)

        calculation_technique = CalculationTechnique(
            type='baranyi_roberts',
            subjectType='strain',
            subjectId=strain.strainId,
            studyUniqueID=study.uuid,
        )
        self.db_session.add(calculation_technique)
        self.db_session.flush()

        self.assertIsNotNone(calculation_technique.id)

        with self.assertRaises(ValueError):
            calculation_technique.type = 'unexpected'
        with self.assertRaises(ValueError):
            calculation_technique.state = 'unexpected'


if __name__ == '__main__':
    unittest.main()

import tests.init  # noqa: F401

import unittest
from decimal import Decimal
import enum

import sqlalchemy as sql

from models.measurement import Measurement
from tests.database_test import DatabaseTest


class TestMeasurement(DatabaseTest):
    def test_successful_creation(self):
        study_id = self.create_study()['studyId']

        bioreplicate_uuid = self.create_bioreplicate(studyId=study_id)['bioreplicateUniqueId']
        strain_id         = self.create_strain(studyId=study_id)['NCBId']

        measurement = Measurement(
            bioreplicateUniqueId=bioreplicate_uuid,
            position='A1',
            timeInSeconds=60,
            pH=Decimal('7.4'),
            unit='Cells/mL',
            technique='FC',
            absoluteValue=Decimal('100_000.0'),
            relativeValue=None,
            subjectType='strain',
            subjectId=strain_id,
        )

        self.assertTrue(measurement.id is None)

        self.db_session.add_all([measurement])
        self.db_session.commit()

        self.assertTrue(measurement.id is not None)

if __name__ == '__main__':
    unittest.main()

import tests.init  # noqa: F401

import unittest
from decimal import Decimal
import enum

import sqlalchemy as sql

from models.measurement import Measurement
from tests.database_test import DatabaseTest
import lib.util as util


class TestMeasurement(DatabaseTest):
    def test_successful_creation(self):
        study_id          = self.create_study()['studyId']
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

    def test_import_growth_and_metabolites_from_csv(self):
        study_id        = self.create_study()['studyId']
        experiment_uuid = self.create_experiment(studyId=study_id)['experimentUniqueId']

        bioreplicate = self.create_bioreplicate(
            studyId=study_id,
            experimentUniqueId=experiment_uuid,
            bioreplicateId='b1',
        )

        strain1_id = self.create_strain(studyId=study_id)['NCBId']
        strain2_id = self.create_strain(studyId=study_id)['NCBId']

        glucose_id = self.create_metabolite_per_experiment(
            studyId=study_id,
            experimentUniqueId=experiment_uuid,
            bioreplicateUniqueId=bioreplicate['bioreplicateUniqueId'],
            metabolite={'metabo_name': 'glucose'},
        )['chebi_id']
        trehalose_id = self.create_metabolite_per_experiment(
            studyId=study_id,
            experimentUniqueId=experiment_uuid,
            bioreplicateUniqueId=bioreplicate['bioreplicateUniqueId'],
            metabolite={'metabo_name': 'trehalose'},
        )['chebi_id']

        growth_and_metabolite_data = util.trim_lines(f"""
            Position,Biological_Replicate_id,Time,FC,glucose,trehalose
            p1,b1,60,1234567890.0,50.0,70.0
            p1,b1,75,234567890.0,30.0,40.0
            p1,b1,90,4567890.0,10.0,10.0
        """)

        measurements = Measurement.insert_from_growth_csv(
            self.db_session,
            experiment_uuid,
            growth_and_metabolite_data,
        )

        # Metabolite measurements
        self.assertEqual(
            [
                (m.timeInSeconds, m.subjectId)
                for m in measurements
                if m.subjectType.value == "metabolite"
            ],
            [
                (60, glucose_id), (60, trehalose_id),
                (75, glucose_id), (75, trehalose_id),
                (90, glucose_id), (90, trehalose_id),
            ]
        )

        # Bioreplicate (total) measurement
        self.assertEqual(
            [
                (m.timeInSeconds, m.subjectId, m.absoluteValue)
                for m in measurements
                if m.subjectType.value == "bioreplicate"
            ],
            [
                (60, bioreplicate['bioreplicateUniqueId'], Decimal('1234567890.00')),
                (75, bioreplicate['bioreplicateUniqueId'], Decimal('234567890.00')),
                (90, bioreplicate['bioreplicateUniqueId'], Decimal('4567890.00')),
            ]
        )


if __name__ == '__main__':
    unittest.main()

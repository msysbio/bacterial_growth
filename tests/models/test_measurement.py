import tests.init  # noqa: F401

import unittest
from decimal import Decimal

from models.experiment import Experiment
from models.measurement import Measurement
from tests.database_test import DatabaseTest
import lib.util as util


class TestMeasurement(DatabaseTest):
    def test_successful_creation(self):
        study_id          = self.create_study()['studyId']
        bioreplicate_uuid = self.create_bioreplicate(studyId=study_id)['bioreplicateUniqueId']
        strain_id         = self.create_strain(studyId=study_id)['NCBId']

        measurement = Measurement(
            studyId=study_id,
            bioreplicateUniqueId=bioreplicate_uuid,
            position='A1',
            timeInSeconds=60 * 3600,
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
        study_id = self.create_study()['studyId']

        bioreplicate = self.create_bioreplicate(
            studyId=study_id,
            bioreplicateId='b1',
        )

        glucose_id = self.create_metabolite_per_experiment(
            studyId=study_id,
            bioreplicateUniqueId=bioreplicate['bioreplicateUniqueId'],
            metabolite={'metabo_name': 'glucose'},
        )['chebi_id']
        trehalose_id = self.create_metabolite_per_experiment(
            studyId=study_id,
            bioreplicateUniqueId=bioreplicate['bioreplicateUniqueId'],
            metabolite={'metabo_name': 'trehalose'},
        )['chebi_id']

        # Note: missing trehalose measurement at t=75
        growth_and_metabolite_data = util.trim_lines("""
            Position,Biological_Replicate_id,Time,FC,glucose,trehalose
            p1,b1,60,1234567890.0,50.0,70.0
            p1,b1,75,234567890.0,30.0,
            p1,b1,90,4567890.0,10.0,10.0
        """)

        measurements = Measurement.insert_from_growth_csv(
            self.db_session,
            study_id,
            growth_and_metabolite_data,
        )

        # Metabolite measurements
        self.assertEqual(
            [
                (m.timeInHours, m.subjectId)
                for m in measurements
                if m.subjectType.value == "metabolite"
            ],
            [
                (60, glucose_id), (60, trehalose_id),
                (75, glucose_id),
                (90, glucose_id), (90, trehalose_id),
            ]
        )

        # Bioreplicate (total) measurement
        self.assertEqual(
            [
                (m.timeInHours, m.subjectId, m.absoluteValue)
                for m in measurements
                if m.subjectType.value == "bioreplicate"
            ],
            [
                (60, bioreplicate['bioreplicateUniqueId'], Decimal('1234567890.00')),
                (75, bioreplicate['bioreplicateUniqueId'], Decimal('234567890.00')),
                (90, bioreplicate['bioreplicateUniqueId'], Decimal('4567890.00')),
            ]
        )

    def test_import_reads_from_csv(self):
        study_id = self.create_study()['studyId']
        bioreplicate = self.create_bioreplicate(
            studyId=study_id,
            bioreplicateId='b1',
        )

        strain1_id = self.create_strain(
            memberName='Bacteroides thetaiotaomicron',
            studyId=study_id,
        )['strainId']
        strain2_id = self.create_strain(
            memberName='Roseburia intestinalis',
            studyId=study_id,
        )['strainId']

        header = ",".join([
            'Position',
            'Biological_Replicate_id',
            'Time',
            'Bacteroides thetaiotaomicron_counts',
            'Roseburia intestinalis_counts',
            'Bacteroides thetaiotaomicron_reads',
            'Bacteroides thetaiotaomicron_reads_std',
            'Roseburia intestinalis_reads',
            'Roseburia intestinalis_reads_std',
        ])

        # Note: missing B. thetaiotaomicron reads and std at t=75
        # Note: missing R. intestinalis reads_std at t=90
        reads_and_counts_data = util.trim_lines(f"""
            {header}
            p1,b1,60,100,200,100.234,10.23,200.456,20.45
            p1,b1,75,200,400,,,400.456,40.45
            p1,b1,90,300,600,300.234,30.23,600.456,
        """)

        measurements = Measurement.insert_from_reads_csv(
            self.db_session,
            study_id,
            reads_and_counts_data,
        )

        # Reads measurements
        # Note: truncated to 2 decimal points
        self.assertEqual(
            [
                (m.timeInHours, int(m.subjectId), m.absoluteValue)
                for m in sorted(measurements, key=lambda m: (m.timeInHours, m.subjectId))
                if m.technique == "16S rRNA-seq"
            ],
            [
                (60, strain1_id, Decimal('100.23')), (60, strain2_id, Decimal('200.46')),
                (75, strain2_id, Decimal('400.46')),
                (90, strain1_id, Decimal('300.23')), (90, strain2_id, Decimal('600.46')),
            ]
        )

        # Counts measurements
        self.assertEqual(
            [
                (m.timeInHours, int(m.subjectId), m.absoluteValue)
                for m in sorted(measurements, key=lambda m: (m.timeInHours, m.subjectId))
                if m.technique == "FC per species"
            ],
            [
                (60, strain1_id, Decimal('100.00')), (60, strain2_id, Decimal('200.00')),
                (75, strain1_id, Decimal('200.00')), (75, strain2_id, Decimal('400.00')),
                (90, strain1_id, Decimal('300.00')), (90, strain2_id, Decimal('600.00')),
            ]
        )


if __name__ == '__main__':
    unittest.main()

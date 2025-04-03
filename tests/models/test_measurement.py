import tests.init  # noqa: F401

import unittest
from decimal import Decimal

from models import (
    Measurement,
    Study
)
from models.measurement_technique import TECHNIQUE_NAMES

from tests.database_test import DatabaseTest
import lib.util as util


class TestMeasurement(DatabaseTest):
    def test_successful_creation(self):
        study_data = self.create_study()
        study = self.db_session.get(Study, study_data['studyUniqueID'])
        study_id = study_data['studyId']

        bioreplicate_uuid = self.create_bioreplicate(studyId=study_id)['bioreplicateUniqueId']
        strain_id         = self.create_strain(studyId=study_id)['NCBId']
        technique         = self.create_measurement_technique(type='fc', subjectType='bioreplicate', studyUniqueID=study.studyUniqueID)

        measurement = Measurement(
            studyId=study.studyId,
            bioreplicateUniqueId=bioreplicate_uuid,
            position='A1',
            timeInSeconds=60 * 3600,
            unit=technique.units,
            techniqueId=technique.id,
            value=Decimal('100_000.0'),
            subjectType='strain',
            subjectId=strain_id,
        )

        self.assertTrue(measurement.id is None)

        self.db_session.add(measurement)
        self.db_session.commit()

        self.assertTrue(measurement.id is not None)

    def test_import_bioreplicate_csv(self):
        study_data = self.create_study(timeUnits='h')
        study = self.db_session.get(Study, study_data['studyUniqueID'])

        study_id = study.studyId
        study_uuid = study.studyUniqueID

        b1 = self.create_bioreplicate(studyId=study_id, bioreplicateId='b1')
        b2 = self.create_bioreplicate(studyId=study_id, bioreplicateId='b2')

        t_fc = self.create_measurement_technique(studyUniqueID=study_uuid, subjectType='bioreplicate', type='fc')
        t_od = self.create_measurement_technique(studyUniqueID=study_uuid, subjectType='bioreplicate', type='od')
        t_ph = self.create_measurement_technique(studyUniqueID=study_uuid, subjectType='bioreplicate', type='ph')

        growth_data = util.trim_lines("""
            Position,Biological_Replicate_id,Time,FC,OD,pH
            p1,b1,2,1234567890.0,0.9,7.4
            p1,b1,4,234567890.0,0.8,7.5
            p1,b2,2,4567890.0,0.7,7.6
            p1,b2,4,4567890.0,0.7,7.6
        """)

        measurements = Measurement.insert_from_bioreplicates_csv(
            self.db_session,
            study,
            growth_data
        )

        # FC measurement
        self.assertEqual(
            [(m.timeInHours, m.subjectId, m.value) for m in measurements if m.techniqueId == t_fc.id],
            [
                (2.0, b1['bioreplicateUniqueId'], Decimal('1234567890.00')),
                (4.0, b1['bioreplicateUniqueId'], Decimal('234567890.00')),
                (2.0, b2['bioreplicateUniqueId'], Decimal('4567890.00')),
                (4.0, b2['bioreplicateUniqueId'], Decimal('4567890.00')),
            ]
        )

        # OD measurements
        self.assertEqual(
            [(m.timeInHours, m.subjectId, m.value) for m in measurements if m.techniqueId == t_od.id],
            [
                (2.0, b1['bioreplicateUniqueId'], Decimal('0.900')),
                (4.0, b1['bioreplicateUniqueId'], Decimal('0.800')),
                (2.0, b2['bioreplicateUniqueId'], Decimal('0.700')),
                (4.0, b2['bioreplicateUniqueId'], Decimal('0.700')),
            ]
        )

        # pH measurements
        self.assertEqual(
            [m.value for m in measurements if m.techniqueId == t_ph.id],
            [Decimal('7.400'), Decimal('7.500'), Decimal('7.600'), Decimal('7.600')]
        )

    def test_import_metabolite_csv(self):
        study_data = self.create_study(timeUnits='m')
        study = self.db_session.get(Study, study_data['studyUniqueID'])

        study_id = study.studyId
        study_uuid = study.studyUniqueID

        b1 = self.create_bioreplicate(studyId=study_id, bioreplicateId='b1')

        glucose_id = self.create_metabolite_per_experiment(
            studyId=study_id,
            bioreplicateUniqueId=b1['bioreplicateUniqueId'],
            metabolite={'metabo_name': 'glucose'},
        )['chebi_id']
        trehalose_id = self.create_metabolite_per_experiment(
            studyId=study_id,
            bioreplicateUniqueId=b1['bioreplicateUniqueId'],
            metabolite={'metabo_name': 'trehalose'},
        )['chebi_id']

        t = self.create_measurement_technique(
            studyUniqueID=study_uuid,
            subjectType='metabolite',
            type='Metabolite',
            metaboliteIds=[glucose_id, trehalose_id],
            units='mM',
        )

        # Note: missing trehalose measurement at t=75
        metabolite_data = util.trim_lines("""
            Position,Biological_Replicate_id,Time,glucose,trehalose
            p1,b1,60,50.0,70.0
            p1,b1,75,30.0,
            p1,b1,90,10.0,10.0
        """)

        measurements = Measurement.insert_from_metabolites_csv(
            self.db_session,
            study,
            metabolite_data
        )

        # Metabolite measurements
        self.assertEqual(
            [(m.timeInSeconds, m.subjectId, m.value) for m in measurements if m.subjectType == "metabolite"],
            [
                (3600, glucose_id, Decimal('50.0')), (3600, trehalose_id, Decimal('70.0')),
                (4500, glucose_id, Decimal('30.0')), (4500, trehalose_id, None),
                (5400, glucose_id, Decimal('10.0')), (5400, trehalose_id, Decimal('10.0')),
            ]
        )

    def test_import_strain_csv(self):
        study_data = self.create_study()
        study = self.db_session.get(Study, study_data['studyUniqueID'])

        study_id = study.studyId
        study_uuid = study.studyUniqueID

        bioreplicate = self.create_bioreplicate(
            studyId=study_id,
            bioreplicateId='b1',
        )

        s1_id = self.create_strain(memberName='B. thetaiotaomicron', studyId=study_id)['strainId']
        s2_id = self.create_strain(memberName='R. intestinalis', studyId=study_id)['strainId']
        strain_ids = [s1_id, s2_id]

        t_fc = self.create_measurement_technique(
            studyUniqueID=study_uuid,
            subjectType='strain',
            type='fc',
            units='Cells/mL',
            strainIds=strain_ids,
        )
        t_16s = self.create_measurement_technique(
            studyUniqueID=study_uuid,
            subjectType='strain',
            type='16s',
            units='reads',
            includeStd=True,
            strainIds=strain_ids,
        )

        header = ",".join([
            'Position',
            'Biological_Replicate_id',
            'Time',
            'B. thetaiotaomicron FC counts',
            'R. intestinalis FC counts',
            'B. thetaiotaomicron rRNA reads',
            'B. thetaiotaomicron rRNA reads STD',
            'R. intestinalis rRNA reads',
            'R. intestinalis rRNA reads STD',
        ])

        # Note: missing B. thetaiotaomicron reads and std at t=75
        # Note: missing R. intestinalis reads_std at t=90
        strain_data = util.trim_lines(f"""
            {header}
            p1,b1,3600,100,200,100.234,10.23,200.456,20.45
            p1,b1,4500,200,400,,,400.456,40.45
            p1,b1,5400,300,600,300.234,30.23,600.456,
        """)

        measurements = Measurement.insert_from_strain_csv(
            self.db_session,
            study,
            strain_data
        )

        # 16s reads
        self.assertEqual(
            [
                (m.timeInSeconds, int(m.subjectId), m.value)
                for m in sorted(measurements, key=lambda m: (m.timeInSeconds, m.subjectId))
                if m.techniqueId == t_16s.id
            ],
            [
                (3600, s1_id, Decimal('100.234')), (3600, s2_id, Decimal('200.456')),
                (4500, s1_id, None),               (4500, s2_id, Decimal('400.456')),
                (5400, s1_id, Decimal('300.234')), (5400, s2_id, Decimal('600.456')),
            ]
        )

        # FC counts
        self.assertEqual(
            [
                (m.timeInSeconds, int(m.subjectId), m.value)
                for m in sorted(measurements, key=lambda m: (m.timeInHours, m.subjectId))
                if m.techniqueId == t_fc.id
            ],
            [
                (3600, s1_id, Decimal('100.00')), (3600, s2_id, Decimal('200.00')),
                (4500, s1_id, Decimal('200.00')), (4500, s2_id, Decimal('400.00')),
                (5400, s1_id, Decimal('300.00')), (5400, s2_id, Decimal('600.00')),
            ]
        )


if __name__ == '__main__':
    unittest.main()

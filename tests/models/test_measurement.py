import tests.init  # noqa: F401

import unittest
from decimal import Decimal

from models import Measurement

from tests.database_test import DatabaseTest
import lib.util as util


class TestMeasurement(DatabaseTest):
    def test_successful_creation(self):
        study = self.create_study()
        study_id = study.studyId

        bioreplicate_id = self.create_bioreplicate(studyId=study_id).id
        compartment_id  = self.create_compartment(studyId=study_id).id
        strain_id       = self.create_strain(studyId=study_id).NCBId
        technique       = self.create_measurement_technique(type='fc', subjectType='bioreplicate', studyUniqueID=study.studyUniqueID)

        measurement = Measurement(
            studyId=study.studyId,
            bioreplicateUniqueId=bioreplicate_id,
            compartmentId=compartment_id,
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
        study = self.create_study(timeUnits='h')

        study_id = study.studyId
        study_uuid = study.studyUniqueID

        b1 = self.create_bioreplicate(studyId=study_id, name='b1')
        b2 = self.create_bioreplicate(studyId=study_id, name='b2')
        self.create_compartment(studyId=study_id, name='c1')

        t_fc = self.create_measurement_technique(studyUniqueID=study_uuid, subjectType='bioreplicate', type='fc')
        t_od = self.create_measurement_technique(studyUniqueID=study_uuid, subjectType='bioreplicate', type='od')
        t_ph = self.create_measurement_technique(studyUniqueID=study_uuid, subjectType='bioreplicate', type='ph')

        growth_data = util.trim_lines("""
            Biological Replicate,Compartment,Time,Community FC,Community OD,Community pH
            b1,c1,2,1234567890.0,0.9,7.4
            b1,c1,4,234567890.0,0.8,7.5
            b2,c1,2,4567890.0,0.7,7.6
            b2,c1,4,4567890.0,0.7,7.6
        """)

        measurements = Measurement.insert_from_csv_string(
            self.db_session,
            study,
            growth_data,
            subject_type='bioreplicate',
        )

        # FC measurement
        self.assertEqual(
            [(m.timeInHours, m.subjectId, m.value) for m in measurements if m.techniqueId == t_fc.id],
            [
                (2.0, str(b1.id), Decimal('1234567890.000')),
                (4.0, str(b1.id), Decimal('234567890.000')),
                (2.0, str(b2.id), Decimal('4567890.000')),
                (4.0, str(b2.id), Decimal('4567890.000')),
            ]
        )

        # OD measurements
        self.assertEqual(
            [(m.timeInHours, m.subjectId, m.value) for m in measurements if m.techniqueId == t_od.id],
            [
                (2.0, str(b1.id), Decimal('0.900')),
                (4.0, str(b1.id), Decimal('0.800')),
                (2.0, str(b2.id), Decimal('0.700')),
                (4.0, str(b2.id), Decimal('0.700')),
            ]
        )

        # pH measurements
        self.assertEqual(
            [m.value for m in measurements if m.techniqueId == t_ph.id],
            [Decimal('7.400'), Decimal('7.500'), Decimal('7.600'), Decimal('7.600')]
        )

    def test_import_metabolite_csv(self):
        study = self.create_study(timeUnits='m')

        study_id = study.studyId
        study_uuid = study.studyUniqueID

        self.create_bioreplicate(studyId=study_id, name='b1')
        self.create_compartment(studyId=study_id, name='c1')

        glucose_id = self.create_study_metabolite(
            studyId=study_id,
            metabolite={'metabo_name': 'glucose'},
        ).chebi_id
        trehalose_id = self.create_study_metabolite(
            studyId=study_id,
            metabolite={'metabo_name': 'trehalose'},
        ).chebi_id

        self.create_measurement_technique(
            studyUniqueID=study_uuid,
            subjectType='metabolite',
            type='Metabolite',
            metaboliteIds=[glucose_id, trehalose_id],
            units='mM',
        )

        # Note: missing trehalose measurement at t=75
        metabolite_data = util.trim_lines("""
            Biological Replicate,Compartment,Time,glucose,trehalose
            b1,c1,60,50.0,70.0
            b1,c1,75,30.0,
            b1,c1,90,10.0,10.0
        """)

        measurements = Measurement.insert_from_csv_string(
            self.db_session,
            study,
            metabolite_data,
            subject_type='metabolite',
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
        study = self.create_study()

        study_id = study.studyId
        study_uuid = study.studyUniqueID

        self.create_bioreplicate(studyId=study_id, name='b1')
        self.create_compartment(studyId=study_id, name='c1')

        s1 = self.create_strain(name='B. thetaiotaomicron', studyId=study_id)
        s2 = self.create_strain(name='R. intestinalis', studyId=study_id)
        strain_ids = [s1.id, s2.id]

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
            'Biological Replicate',
            'Compartment',
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
            b1,c1,3600,100,200,100.234,10.23,200.456,20.45
            b1,c1,4500,200,400,,,400.456,40.45
            b1,c1,5400,300,600,300.234,30.23,600.456,
        """)

        measurements = Measurement.insert_from_csv_string(
            self.db_session,
            study,
            strain_data,
            subject_type='strain',
        )

        # 16s reads
        self.assertEqual(
            [
                (m.timeInSeconds, int(m.subjectId), m.value)
                for m in sorted(measurements, key=lambda m: (m.timeInSeconds, m.subjectId))
                if m.techniqueId == t_16s.id
            ],
            [
                (3600, s1.id, Decimal('100.234')), (3600, s2.id, Decimal('200.456')),
                (4500, s1.id, None),               (4500, s2.id, Decimal('400.456')),
                (5400, s1.id, Decimal('300.234')), (5400, s2.id, Decimal('600.456')),
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
                (3600, s1.id, Decimal('100.00')), (3600, s2.id, Decimal('200.00')),
                (4500, s1.id, Decimal('200.00')), (4500, s2.id, Decimal('400.00')),
                (5400, s1.id, Decimal('300.00')), (5400, s2.id, Decimal('600.00')),
            ]
        )


if __name__ == '__main__':
    unittest.main()

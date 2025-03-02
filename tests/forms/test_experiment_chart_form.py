import tests.init

import unittest

from tests.database_test import DatabaseTest
from forms.experiment_chart_form import ExperimentChartForm
from models.experiment import Experiment

class TestExperimentChartForm(DatabaseTest):
    def test_metabolite_chart(self):
        bioreplicate = self.create_bioreplicate()

        study_id          = bioreplicate['studyId']
        bioreplicate_uuid = bioreplicate['bioreplicateUniqueId']

        experiment = self.db_session.get(Experiment, bioreplicate['experimentUniqueId'])
        chart = ExperimentChartForm(experiment)

        self.create_metabolite(chebi_id='1', metabo_name='glucose')
        self.create_metabolite(chebi_id='2', metabo_name='trehalose')

        shared_params = {
            'studyId': study_id,
            'bioreplicateUniqueId': bioreplicate_uuid,
            'technique': 'FC',
            'absoluteValue': 200.0,
        }
        self.create_measurement(subjectId='1', subjectType='metabolite', timeInSeconds=3600, **shared_params)
        self.create_measurement(subjectId='1', subjectType='metabolite', timeInSeconds=7200, **shared_params)
        self.create_measurement(subjectId='2', subjectType='metabolite', timeInSeconds=3600, **shared_params)
        self.create_measurement(subjectId='2', subjectType='metabolite', timeInSeconds=7200, **shared_params)

        # Not included:
        other_params = {**shared_params, 'technique': 'OD'}
        self.create_measurement(subjectId='2', subjectType='metabolite', timeInSeconds=3600, **other_params)
        other_params = {**shared_params, 'subjectType': 'other'}
        self.create_measurement(subjectId='2', timeInSeconds=3600, **other_params)

        self.db_session.commit()

        chart_df = chart.get_df([bioreplicate_uuid], technique='FC', subject_type='metabolite')

        self.assertEqual(chart_df['time'].tolist(), [1, 2, 1, 2])
        self.assertEqual(
            list(map(str, chart_df['value'].tolist())),
            ['200.0', '200.0', '200.0', '200.0'],
        )
        self.assertEqual(chart_df['subjectName'].tolist(), ['glucose', 'glucose', 'trehalose', 'trehalose'])

    def test_strain_chart(self):
        bioreplicate = self.create_bioreplicate()

        study_id          = bioreplicate['studyId']
        bioreplicate_uuid = bioreplicate['bioreplicateUniqueId']

        experiment = self.db_session.get(Experiment, bioreplicate['experimentUniqueId'])
        chart = ExperimentChartForm(experiment)

        self.create_strain(strainId=1, memberName='R. intestinalis',     studyId=study_id)
        self.create_strain(strainId=2, memberName='B. thetaiotaomicron', studyId=study_id)

        shared_params = {
            'studyId': study_id,
            'bioreplicateUniqueId': bioreplicate_uuid,
            'technique': '16S',
            'absoluteValue': 200.0,
        }
        self.create_measurement(subjectId='1', subjectType='strain', timeInSeconds=3600, **shared_params)
        self.create_measurement(subjectId='1', subjectType='strain', timeInSeconds=7200, **shared_params)
        self.create_measurement(subjectId='2', subjectType='strain', timeInSeconds=3600, **shared_params)
        self.create_measurement(subjectId='2', subjectType='strain', timeInSeconds=7200, **shared_params)

        # Not included:
        other_params = {**shared_params, 'technique': 'OD'}
        self.create_measurement(subjectId='2', subjectType='strain', timeInSeconds=3600, **other_params)
        other_params = {**shared_params, 'subjectType': 'other'}
        self.create_measurement(subjectId='2', timeInSeconds=3600, **other_params)

        self.db_session.commit()

        chart_df = chart.get_df([bioreplicate_uuid], technique='16S', subject_type='strain')

        self.assertEqual(chart_df['time'].tolist(), [1, 2, 1, 2])
        self.assertEqual(
            list(map(str, chart_df['value'].tolist())),
            ['200.0', '200.0', '200.0', '200.0'],
        )

        self.assertEqual(
            chart_df['subjectName'].tolist(),
            ['B. thetaiotaomicron', 'B. thetaiotaomicron', 'R. intestinalis', 'R. intestinalis'],
        )


if __name__ == '__main__':
    unittest.main()

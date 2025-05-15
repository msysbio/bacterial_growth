import tests.init  # noqa: F401

import unittest

from tests.database_test import DatabaseTest
from forms.experiment_chart_form import ExperimentChartForm
from models import Experiment


class TestExperimentChartForm(DatabaseTest):
    def test_df_for_metabolite_chart(self):
        bioreplicate = self.create_bioreplicate()

        study_id          = bioreplicate.studyId
        bioreplicate_uuid = bioreplicate.id

        experiment = self.db_session.get(Experiment, bioreplicate.experimentId)
        chart = ExperimentChartForm(experiment)

        self.create_metabolite(chebi_id='1', metabo_name='glucose')
        self.create_metabolite(chebi_id='2', metabo_name='trehalose')

        shared_params = {
            'studyId': study_id,
            'bioreplicateUniqueId': bioreplicate_uuid,
            'value': 200.0,
            'technique': 'Metabolites',
            'measurementTechnique': {
                'type': 'metabolite',
                'subjectType': 'metabolite',
            }
        }
        self.create_measurement(context={'subjectId': '1', 'subjectType': 'metabolite'}, timeInSeconds=3600, **shared_params)
        self.create_measurement(context={'subjectId': '1', 'subjectType': 'metabolite'}, timeInSeconds=7200, **shared_params)
        self.create_measurement(context={'subjectId': '2', 'subjectType': 'metabolite'}, timeInSeconds=3600, **shared_params)
        self.create_measurement(context={'subjectId': '2', 'subjectType': 'metabolite'}, timeInSeconds=7200, **shared_params)

        self.db_session.commit()

        chart_df = chart.get_df([bioreplicate_uuid], technique='Metabolites', subject_type='metabolite')

        self.assertEqual(chart_df['time'].tolist(), [1, 2, 1, 2])
        self.assertEqual(
            list(map(str, chart_df['value'].tolist())),
            ['200.0', '200.0', '200.0', '200.0'],
        )
        self.assertEqual(chart_df['subjectName'].tolist(), ['glucose', 'glucose', 'trehalose', 'trehalose'])

    def test_df_for_strain_chart(self):
        bioreplicate = self.create_bioreplicate()

        study_id          = bioreplicate.studyId
        bioreplicate_uuid = bioreplicate.id

        experiment = self.db_session.get(Experiment, bioreplicate.experimentId)
        chart = ExperimentChartForm(experiment)

        s1 = self.create_strain(name='R. intestinalis',     studyId=study_id)
        s2 = self.create_strain(name='B. thetaiotaomicron', studyId=study_id)

        shared_params = {
            'studyId': study_id,
            'value': 200.0,
        }
        shared_context = {
            'studyId': study_id,
            'bioreplicateId': bioreplicate_uuid,
            'subjectType': 'strain',
            'measurement_technique': {
                'type': '16s',
                'subjectType': 'strain',
            }
        }
        self.create_measurement(measurement_context={'subjectId': s1.id, **shared_context}, timeInSeconds=3600, **shared_params)
        self.create_measurement(measurement_context={'subjectId': s1.id, **shared_context}, timeInSeconds=7200, **shared_params)
        self.create_measurement(measurement_context={'subjectId': s2.id, **shared_context}, timeInSeconds=3600, **shared_params)
        self.create_measurement(measurement_context={'subjectId': s2.id, **shared_context}, timeInSeconds=7200, **shared_params)

        self.db_session.commit()

        chart_df = chart.get_df([bioreplicate_uuid], technique='16S rRNA-seq', subject_type='strain')

        self.assertEqual(chart_df['time'].tolist(), [1, 2, 1, 2])
        self.assertEqual(
            list(map(str, chart_df['value'].tolist())),
            ['200.0', '200.0', '200.0', '200.0'],
        )

        self.assertEqual(
            chart_df['subjectName'].tolist(),
            ['B. thetaiotaomicron', 'B. thetaiotaomicron', 'R. intestinalis', 'R. intestinalis'],
        )

    def test_average_df_for_strain_chart(self):
        experiment      = self.create_experiment()
        study_id        = experiment.studyId
        experiment_uuid = experiment.id

        bioreplicate1 = self.create_bioreplicate(experimentId=experiment_uuid, studyId=study_id)
        bioreplicate2 = self.create_bioreplicate(experimentId=experiment_uuid, studyId=study_id)

        s1 = self.create_strain(name='R. intestinalis', studyId=study_id)

        experiment = self.db_session.get(Experiment, experiment_uuid)
        chart = ExperimentChartForm(experiment)

        shared_params = {
            'studyId': study_id,
            'subjectId': s1.id,
            'subjectType': 'strain',
            # TODO (2025-04-02) Remove technique, use id
            'technique': '16S rRNA-seq',
            'measurementTechnique': {
                'type': '16s',
                'subjectType': 'strain',
            }
        }

        # First time point:
        self.create_measurement(
            bioreplicateUniqueId=bioreplicate1.id,
            timeInSeconds=3600,
            value=100.0,
            **shared_params,
        )
        self.create_measurement(
            bioreplicateUniqueId=bioreplicate2.id,
            timeInSeconds=3600,
            value=200.0,
            **shared_params,
        )

        # Second time point:
        self.create_measurement(
            bioreplicateUniqueId=bioreplicate1.id,
            timeInSeconds=7200,
            value=200.0,
            **shared_params,
        )
        self.create_measurement(
            bioreplicateUniqueId=bioreplicate2.id,
            timeInSeconds=7200,
            value=250.0,
            **shared_params,
        )

        self.db_session.commit()

        chart_df = chart.get_average_df(technique='16S rRNA-seq', subject_type='strain')

        self.assertEqual(chart_df['time'].tolist(), [1, 2])
        self.assertEqual(chart_df['value'].tolist(), [150.0, 225.0])

    def test_average_df_for_bioreplicate_chart(self):
        experiment      = self.create_experiment()
        study_id        = experiment.studyId
        experiment_uuid = experiment.id

        bioreplicate1 = self.create_bioreplicate(experimentId=experiment_uuid, studyId=study_id)
        bioreplicate2 = self.create_bioreplicate(experimentId=experiment_uuid, studyId=study_id)

        self.create_strain(name='R. intestinalis', studyId=study_id)

        experiment = self.db_session.get(Experiment, experiment_uuid)
        chart = ExperimentChartForm(experiment)

        shared_params = {
            'studyId': study_id,
            'technique': '16S rRNA-seq',
            'measurementTechnique': {
                'type': '16s',
                'subjectType': 'bioreplicate',
            }
        }

        # First time point:
        self.create_measurement(
            bioreplicateUniqueId=bioreplicate1.id,
            subjectId=bioreplicate1.id,
            subjectType='bioreplicate',
            timeInSeconds=3600,
            value=200.0,
            **shared_params,
        )
        self.create_measurement(
            bioreplicateUniqueId=bioreplicate2.id,
            subjectId=bioreplicate2.id,
            subjectType='bioreplicate',
            timeInSeconds=3600,
            value=300.0,
            **shared_params,
        )

        # Second time point:
        self.create_measurement(
            bioreplicateUniqueId=bioreplicate1.id,
            subjectId=bioreplicate1.id,
            subjectType='bioreplicate',
            timeInSeconds=7200,
            value=100.0,
            **shared_params,
        )
        self.create_measurement(
            bioreplicateUniqueId=bioreplicate2.id,
            subjectId=bioreplicate2.id,
            subjectType='bioreplicate',
            timeInSeconds=7200,
            value=350.0,
            **shared_params,
        )

        self.db_session.commit()

        chart_df = chart.get_average_df(technique='16S rRNA-seq', subject_type='bioreplicate')

        self.assertEqual(chart_df['time'].tolist(), [1, 2])
        self.assertEqual(chart_df['value'].tolist(), [250.0, 225.0])


if __name__ == '__main__':
    unittest.main()

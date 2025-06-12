import tests.init  # noqa: F401

import unittest

from app.model.lib.modeling_tasks import _process_modeling_request
from tests.database_test import DatabaseTest


class TestModelingTasks(DatabaseTest):
    def test_modeling_request_status_change(self):
        modeling_request = self.create_modeling_request(state='error')

        _process_modeling_request(self.db_session, modeling_request.id, [])
        self.assertEqual(modeling_request.state, 'ready')

    def test_baranyi_roberts_calculation(self):
        strain              = self.create_strain()
        measurement_context = self.create_measurement_context(subjectId=strain.id, subjectType='strain')
        modeling_request    = self.create_modeling_request()

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
            self.create_measurement(
                contextId=measurement_context.id,
                timeInSeconds=(hours * 3600),
                value=value,
            )

        _process_modeling_request(self.db_session, modeling_request.id, [measurement_context.id])

        self.assertEqual(len(modeling_request.results), 1)

        modeling_result = modeling_request.results[0]
        self.assertEqual(len(modeling_result.coefficients), 4)
        self.assertEqual(set(modeling_result.coefficients.keys()), {'y0', 'h0', 'K', 'mumax'})


if __name__ == '__main__':
    unittest.main()

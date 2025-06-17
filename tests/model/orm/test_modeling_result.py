import tests.init  # noqa: F401

import unittest

from app.model.orm import ModelingResult
from tests.database_test import DatabaseTest


class TestModelingResult(DatabaseTest):
    def test_successful_creation(self):
        strain              = self.create_strain()
        measurement_context = self.create_measurement_context(subjectId=strain.id, subjectType='strain')
        modeling_request    = self.create_modeling_request()

        modeling_result = ModelingResult(
            type='baranyi_roberts',
            measurementContextId=measurement_context.id,
            requestId=modeling_request.id,
        )
        self.db_session.add(modeling_result)
        self.db_session.flush()

        self.assertIsNotNone(modeling_result.id)
        self.assertEqual(modeling_result.state, 'pending')

        with self.assertRaises(ValueError):
            modeling_request.type = 'unexpected'
        with self.assertRaises(ValueError):
            modeling_request.state = 'unexpected'


if __name__ == '__main__':
    unittest.main()

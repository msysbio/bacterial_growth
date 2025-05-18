import tests.init  # noqa: F401

import unittest

from models import ModelingRequest
from tests.database_test import DatabaseTest


class TestModelingRequest(DatabaseTest):
    def test_successful_creation(self):
        study  = self.create_study()

        modeling_request = ModelingRequest(
            type='baranyi_roberts',
            studyUniqueID=study.uuid,
        )
        self.db_session.add(modeling_request)
        self.db_session.flush()

        self.assertIsNotNone(modeling_request.id)
        self.assertEqual(modeling_request.state, 'pending')

        with self.assertRaises(ValueError):
            modeling_request.type = 'unexpected'
        with self.assertRaises(ValueError):
            modeling_request.state = 'unexpected'


if __name__ == '__main__':
    unittest.main()

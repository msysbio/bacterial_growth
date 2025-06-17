import tests.init  # noqa: F401

import unittest

from app.model.orm import Compartment
from tests.database_test import DatabaseTest


class TestCompartment(DatabaseTest):
    def test_successful_creation(self):
        study = self.create_study()

        compartment = Compartment(
            studyId=study.publicId,
            name="Test compartment",
            mediumName='Wilkins-Chalgren Anaerobe Broth (WC)',
        )
        self.db_session.add(compartment)
        self.db_session.flush()

        self.assertIsNotNone(compartment.id)


if __name__ == '__main__':
    unittest.main()

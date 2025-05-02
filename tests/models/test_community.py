import tests.init  # noqa: F401

import unittest
from decimal import Decimal

from models import Community

from tests.database_test import DatabaseTest

class TestCommunity(DatabaseTest):
    def test_successful_creation(self):
        study = self.create_study()
        strain1 = self.create_strain(studyId=study.publicId)
        strain2 = self.create_strain(studyId=study.publicId)

        community = Community(
            studyId=study.publicId,
            name="Test community",
            strainIds=[strain1.id, strain2.id],
        )
        self.db_session.add(community)
        self.db_session.flush()

        self.assertIsNotNone(community.id)


if __name__ == '__main__':
    unittest.main()

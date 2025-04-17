import tests.init  # noqa: F401

import unittest
import datetime
from types import SimpleNamespace

import sqlalchemy as sql

from models import Study
from tests.database_test import DatabaseTest


class TestStudy(DatabaseTest):
    def test_user_visibility(self):
        study = self.create_study(publishedAt=None, publishableAt=datetime.datetime.now())
        self.create_study_user(studyUniqueID=study.uuid, userUniqueID='user1')
        self.create_study_user(studyUniqueID=study.uuid, userUniqueID='user2')
        self.db_session.flush()

        # Unpublished: only visible to linked users:
        self.assertFalse(study.visibleToUser(None))
        self.assertFalse(study.visibleToUser(SimpleNamespace(uuid='user3')))

        self.assertTrue(study.visibleToUser(SimpleNamespace(uuid='user1')))
        self.assertTrue(study.visibleToUser(SimpleNamespace(uuid='user2')))

        self.assertTrue(study.publish())

        # Published: visible to all users:
        self.assertTrue(study.visibleToUser(None))
        self.assertTrue(study.visibleToUser(SimpleNamespace(uuid='user3')))
        self.assertTrue(study.visibleToUser(SimpleNamespace(uuid='user1')))
        self.assertTrue(study.visibleToUser(SimpleNamespace(uuid='user2')))

    def test_generating_available_id(self):
        # The first ID in an empty database should be 001:
        public_id = Study.find_available_id(self.db_session)
        self.assertEqual(public_id, "SMGDB00000001")

        self.create_study(studyId="SMGDB00000001")

        public_id = Study.find_available_id(self.db_session)
        self.assertEqual(public_id, "SMGDB00000002")

        self.create_study(studyId="SMGDB00000002")
        self.create_study(studyId="SMGDB00000003")

        # Deleting a project should not generate duplicate ids:
        self.db_session.execute(
            sql.delete(Study)
            .where(Study.publicId == "SMGDB00000002")
        )

        public_id = Study.find_available_id(self.db_session)
        self.assertEqual(public_id, "SMGDB00000004")


if __name__ == '__main__':
    unittest.main()

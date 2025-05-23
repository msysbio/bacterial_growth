import tests.init  # noqa: F401

import unittest
from datetime import datetime, timedelta, UTC
from types import SimpleNamespace

import sqlalchemy as sql

from app.model.orm import Study
from tests.database_test import DatabaseTest


class TestStudy(DatabaseTest):
    def test_user_visibility(self):
        study = self.create_study(publishedAt=None, publishableAt=datetime.now(UTC))
        self.create_study_user(studyUniqueID=study.uuid, userUniqueID='user1')
        self.create_study_user(studyUniqueID=study.uuid, userUniqueID='user2')
        self.db_session.flush()

        # Unpublished: only visible to linked users:
        self.assertFalse(study.visible_to_user(None))
        self.assertFalse(study.visible_to_user(SimpleNamespace(uuid='user3')))

        self.assertTrue(study.visible_to_user(SimpleNamespace(uuid='user1')))
        self.assertTrue(study.visible_to_user(SimpleNamespace(uuid='user2')))

        self.assertTrue(study.publish())

        # Published: visible to all users:
        self.assertTrue(study.visible_to_user(None))
        self.assertTrue(study.visible_to_user(SimpleNamespace(uuid='user3')))
        self.assertTrue(study.visible_to_user(SimpleNamespace(uuid='user1')))
        self.assertTrue(study.visible_to_user(SimpleNamespace(uuid='user2')))

    def test_generating_available_id(self):
        # The first ID in an empty database should be 001:
        public_id = Study.generate_public_id(self.db_session)
        self.assertEqual(public_id, "SMGDB00000001")

        self.create_study(studyId="SMGDB00000001")

        public_id = Study.generate_public_id(self.db_session)
        self.assertEqual(public_id, "SMGDB00000002")

        self.create_study(studyId="SMGDB00000002")
        self.create_study(studyId="SMGDB00000003")

        # Deleting a project should not generate duplicate ids:
        self.db_session.execute(
            sql.delete(Study)
            .where(Study.publicId == "SMGDB00000002")
        )

        public_id = Study.generate_public_id(self.db_session)
        self.assertEqual(public_id, "SMGDB00000004")

    def test_find_last_submission(self):
        study = self.create_study()

        self.assertIsNone(study.find_last_submission(self.db_session))

        _s1 = self.create_submission(studyUniqueID=study.uuid, updatedAt=(datetime.now(UTC) - timedelta(hours=24)))
        s2  = self.create_submission(studyUniqueID=study.uuid, updatedAt=(datetime.now(UTC) - timedelta(hours=12)))
        _s3 = self.create_submission(studyUniqueID=study.uuid, updatedAt=(datetime.now(UTC) - timedelta(hours=48)))

        self.assertEqual(study.find_last_submission(self.db_session), s2)
        s4 = self.create_submission(studyUniqueID=study.uuid, updatedAt=(datetime.now(UTC) - timedelta(hours=6)))

        self.assertEqual(study.find_last_submission(self.db_session), s4)


if __name__ == '__main__':
    unittest.main()

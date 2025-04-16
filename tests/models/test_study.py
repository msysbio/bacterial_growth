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
        study_user1 = self.create_study_user(studyUniqueID=study.uuid, userUniqueID='user1')
        study_user2 = self.create_study_user(studyUniqueID=study.uuid, userUniqueID='user2')
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


if __name__ == '__main__':
    unittest.main()

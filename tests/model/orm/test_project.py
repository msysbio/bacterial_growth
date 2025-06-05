import tests.init  # noqa: F401

import sqlalchemy as sql

from app.model.orm import Project
from tests.database_test import DatabaseTest


class TestProject(DatabaseTest):
    def test_generating_available_id(self):
        # The first ID in an empty database should be 001:
        public_id = Project.generate_public_id(self.db_session)
        self.assertEqual(public_id, "PMGDB000001")

        self.create_project(projectId="PMGDB000001")

        public_id = Project.generate_public_id(self.db_session)
        self.assertEqual(public_id, "PMGDB000002")

        self.create_project(projectId="PMGDB000002")
        self.create_project(projectId="PMGDB000003")

        # Deleting a project should not generate duplicate ids:
        self.db_session.execute(
            sql.delete(Project)
            .where(Project.publicId == "PMGDB000002")
        )

        public_id = Project.generate_public_id(self.db_session)
        self.assertEqual(public_id, "PMGDB000004")

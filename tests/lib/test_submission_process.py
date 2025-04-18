import unittest
from datetime import datetime, timedelta, UTC
from freezegun import freeze_time

from models import (
    Submission,
    Study,
    Project,
)
from forms.submission_form import SubmissionForm
from lib.submission_process import (
    _save_project,
    _save_study,
)
from tests.database_test import DatabaseTest

class TestSubmissionProcess(DatabaseTest):
    def test_project_and_study_creation(self):
        submission = self.create_submission(
            studyDesign={
                'project': {'name': 'Test project'},
                'study':   {'name': 'Test study'}
            }
        )
        self.db_session.add(submission)
        self.db_session.flush()

        submission_form = SubmissionForm(submission_id=submission.id, db_session=self.db_session)

        # Creating a new project and study:
        project = self.db_session.get(Project, submission.projectUniqueID)
        study   = self.db_session.get(Study,   submission.studyUniqueID)
        self.assertIsNone(project)
        self.assertIsNone(study)

        _save_project(self.db_session, submission_form)
        _save_study(self.db_session, submission_form)
        self.db_session.flush()

        project = self.db_session.get(Project, submission.projectUniqueID)
        study   = self.db_session.get(Study,   submission.studyUniqueID)
        self.assertIsNotNone(project)
        self.assertIsNotNone(study)
        self.assertEqual(project.name, 'Test project')
        self.assertEqual(study.name, 'Test study')

        # Updating the existing project and study:
        submission_form.update_project({
            'project_uuid': submission.projectUniqueID,
            'study_uuid':   submission.studyUniqueID,
            'study_name':   'Updated study name',
            'project_name': 'Updated project name',
        })

        # Save the study, the project is not updated yet:
        _save_study(self.db_session, submission_form)
        self.db_session.flush()

        self.assertEqual(project.name, 'Test project')
        self.assertEqual(study.name, 'Updated study name')

        # Save project, both names are updated:
        _save_project(self.db_session, submission_form)
        self.db_session.flush()

        self.assertEqual(project.name, 'Updated project name')
        self.assertEqual(study.name, 'Updated study name')

    def test_study_publication_state(self):
        submission = self.create_submission()
        self.db_session.add(submission)
        self.db_session.flush()

        submission_form = SubmissionForm(submission_id=submission.id, db_session=self.db_session)

        with freeze_time(datetime.now(UTC)) as frozen_time:
            _save_project(self.db_session, submission_form)
            _save_study(self.db_session, submission_form)
            self.db_session.flush()

            project = self.db_session.get(Project, submission.projectUniqueID)
            study   = self.db_session.get(Study,   submission.studyUniqueID)

            # Initial study state: not published, can't be published
            self.assertFalse(study.isPublishable)
            self.assertFalse(study.isPublished)
            self.assertFalse(study.publish())

            # After 24 hours, it can be published:
            frozen_time.tick(delta=timedelta(hours=24, seconds=1))

            self.assertTrue(study.isPublishable)
            self.assertFalse(study.isPublished)

            # After explicitly publishing, it's published
            self.assertTrue(study.publish())
            self.db_session.add(study)
            self.db_session.commit()

            self.assertTrue(study.isPublishable)
            self.assertTrue(study.isPublished)


if __name__ == '__main__':
    unittest.main()

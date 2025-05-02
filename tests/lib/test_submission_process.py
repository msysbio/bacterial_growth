import tests.init  # noqa: F401

import unittest
from datetime import datetime, timedelta, UTC

from freezegun import freeze_time
import sqlalchemy as sql

from models import (
    Community,
    Compartment,
    Project,
    Study,
    Strain,
)
from forms.submission_form import SubmissionForm
from lib.submission_process import (
    _save_project,
    _save_study,
    _save_compartments,
    _save_communities,
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

            study = self.db_session.get(Study, submission.studyUniqueID)

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

    def test_compartment_creation(self):
        submission = self.create_submission(
            studyDesign={
                'project': {'name': 'Test project'},
                'study':   {'name': 'Test study'},

                'compartments': [{
                    'name': 'WC',
                    'mediumName': 'Wilkins-Chalgren',
                }, {
                    'name': 'Mucin',
                    'mediumName': 'Mucin',
                }]
            }
        )
        self.db_session.add(submission)
        self.db_session.flush()

        submission_form = SubmissionForm(submission_id=submission.id, db_session=self.db_session)

        # Creating compartments defined by the submission
        study        = _save_study(self.db_session, submission_form)
        compartments = _save_compartments(self.db_session, submission_form, study)

        self.db_session.flush()

        self.assertEqual(['WC', 'Mucin'], [c.name for c in compartments])
        self.assertEqual(compartments, study.compartments)
        self.assertEqual(2, self.db_session.scalar(sql.func.count(Compartment.id)))

        # Remove all compartments
        submission.studyDesign['compartments'] = []
        compartments = _save_compartments(self.db_session, submission_form, study)

        self.db_session.flush()
        self.db_session.refresh(study)

        self.assertEqual([], [c.name for c in compartments])
        self.assertEqual(compartments, study.compartments)
        self.assertEqual(0, self.db_session.scalar(sql.func.count(Compartment.id)))

    def test_community_creation(self):
        t_ri = self.create_taxon(tax_names='Roseburia intestinalis')
        t_bh = self.create_taxon(tax_names='Blautia hydrogenotrophica')

        submission = self.create_submission(
            studyDesign={
                'project': {'name': 'Test project'},
                'study':   {'name': 'Test study'},

                'new_strains': [{
                    'name': 'Custom strain',
                    'description': 'test',
                    'species': t_ri.tax_id,
                }],

                'communities': [{
                    'name': 'Full',
                    'strainIdentifiers': [
                        f"existing|{t_ri.id}",
                        f"existing|{t_bh.id}",
                        'custom|Custom strain',
                    ],
                }, {
                    'name': 'RI',
                    'strainIdentifiers': [f"existing|{t_ri.id}"]
                }, {
                    'name': 'Blank',
                    'strainIdentifiers': [],
                }]
            }
        )
        self.db_session.add(submission)
        self.db_session.flush()

        submission_form = SubmissionForm(submission_id=submission.id, db_session=self.db_session)

        # Creating compartments defined by the submission
        study       = _save_study(self.db_session, submission_form)
        communities = _save_communities(self.db_session, submission_form, study, user_uuid='user1')

        self.db_session.flush()

        self.assertEqual(['Full', 'RI', 'Blank'], [c.name for c in communities])
        self.assertEqual(communities, study.communities)
        self.assertEqual(3, self.db_session.scalar(sql.func.count(Community.id)))

        # Check existence of strains:
        s_ri     = self.db_session.scalar(sql.select(Strain).where(Strain.NCBId == t_ri.tax_id))
        s_bh     = self.db_session.scalar(sql.select(Strain).where(Strain.NCBId == t_bh.tax_id))
        s_custom = self.db_session.scalar(sql.select(Strain).where(Strain.name == 'Custom strain'))

        c_full, c_ri, c_blank = communities
        self.assertEqual(set(c_full.strainIds), {s_ri.id, s_bh.id, s_custom.id})

        # Remove all communities
        submission.studyDesign['communities'] = []
        communities = _save_communities(self.db_session, submission_form, study, user_uuid='user1')

        self.db_session.flush()
        self.db_session.refresh(study)

        self.assertEqual([], [c.name for c in communities])
        self.assertEqual(communities, study.communities)
        self.assertEqual(0, self.db_session.scalar(sql.func.count(Community.id)))


if __name__ == '__main__':
    unittest.main()

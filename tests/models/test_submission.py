import tests.init  # noqa: F401

import unittest

import sqlalchemy as sql

from tests.database_test import DatabaseTest
from models import Submission


class TestSubmission(DatabaseTest):
    def test_project_and_studies(self):
        p1 = self.create_project(projectName="Project 1")
        p2 = self.create_project(projectName="Project 2")
        s2 = self.create_study(projectUniqueID=p2['projectUniqueID'])

        submission = Submission({}, step=1, db_conn=self.db_conn)
        self.assertEqual(submission.project_id, None)
        # No project, no study
        self.assertEqual(submission.type, 'new_project')

        submission = Submission({'project_uuid': p1['projectUniqueID']}, step=1, db_conn=self.db_conn)
        self.assertEqual(submission.project_id, p1['projectId'])
        # Project present, but no study:
        self.assertEqual(submission.type, 'new_study')

        submission = Submission(
            {
                'project_uuid': p2['projectUniqueID'],
                'study_uuid': s2['studyUniqueID'],
            },
            step=1,
            db_conn=self.db_conn,
        )
        self.assertEqual(submission.project_id, p2['projectId'])
        self.assertEqual(submission.study_id, s2['studyId'])
        # Both project and study present:
        self.assertEqual(submission.type, 'update_study')


    def test_strains(self):
        t1 = self.create_taxon(tax_names="R. intestinalis")
        t2 = self.create_taxon(tax_names="B. thetaiotaomicron")

        submission = Submission({}, step=1, db_conn=self.db_conn)
        self.assertEqual(submission.fetch_taxa(), [])

        submission = Submission({'strains': [t1['tax_id']]}, step=1, db_conn=self.db_conn)
        self.assertEqual(
            [t.tax_names for t in submission.fetch_taxa()],
            ['R. intestinalis'],
        )

        submission.update_strains({'strains': [t1['tax_id'], t2['tax_id']], 'new_strains': []})
        self.assertEqual(
            [t.tax_names for t in submission.fetch_taxa()],
            ['R. intestinalis', 'B. thetaiotaomicron'],
        )

        new_strains = [
            {'name': 'R. intestinalis 2',     'species': t1['tax_id']},
            {'name': 'B. thetaiotaomicron 2', 'species': t2['tax_id']},
            {'name': 'R. intestinalis 3',     'species': t1['tax_id']},
            {'name': 'Nonexistent',           'species': '999'},
        ]
        submission.update_strains({'strains': [], 'new_strains': new_strains})

        self.assertEqual(
            sorted([(s['name'], s['species_name']) for s in submission.fetch_new_strains()]),
            sorted([
                ('R. intestinalis 2',     'R. intestinalis'),
                ('R. intestinalis 3',     'R. intestinalis'),
                ('B. thetaiotaomicron 2', 'B. thetaiotaomicron'),
                ('Nonexistent',           None),
            ]),
        )

    def test_metabolites(self):
        m1 = self.create_metabolite(metabo_name="glucose")
        m2 = self.create_metabolite(metabo_name="trehalose")

        submission = Submission({}, step=1, db_conn=self.db_conn)
        self.assertEqual(submission.fetch_taxa(), [])

        submission = Submission({'metabolites': [m1['chebi_id']]}, step=1, db_conn=self.db_conn)
        self.assertEqual(
            [m.metabo_name for m in submission.fetch_metabolites()],
            ['glucose'],
        )

        submission = Submission(
            {'metabolites': [m1['chebi_id'], m2['chebi_id']]},
            step=1,
            db_conn=self.db_conn,
        )
        self.assertEqual(
            [m.metabo_name for m in submission.fetch_metabolites()],
            ['glucose', 'trehalose'],
        )


if __name__ == '__main__':
    unittest.main()

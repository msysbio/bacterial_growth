import tests.init  # noqa: F401

import unittest

import sqlalchemy as sql

from tests.database_test import DatabaseTest
from forms.submission_form import SubmissionForm


class TestSubmissionForm(DatabaseTest):
    def test_project_and_studies(self):
        p1 = self.create_project(projectName="Project 1")
        p2 = self.create_project(projectName="Project 2")
        s2 = self.create_study(projectUniqueID=p2['projectUniqueID'])

        submission_form = SubmissionForm(db_session=self.db_session)
        self.assertEqual(submission_form.project_id, None)
        # No project, no study
        self.assertEqual(submission_form.type, 'new_project')

        submission_form.update_project({
            'submission_type':     'new_study',
            'project_uuid':        p1['projectUniqueID'],
            'project_name':        'Project 1 (updated)',
            'project_description': 'Test',
        })

        self.assertEqual(submission_form.project_id, p1['projectId'])
        self.assertEqual(submission_form.type, 'new_study')
        self.assertEqual(submission_form.submission.studyDesign['project']['name'], 'Project 1 (updated)')

        submission_form.update_project({
            'submission_type':     'update_study',
            'project_uuid':        p2['projectUniqueID'],
            'study_uuid':          s2['studyUniqueID'],
            'project_name':        'Project 2 (updated)',
            'project_description': 'Test',
        })

        self.assertEqual(submission_form.project_id, p2['projectId'])
        self.assertEqual(submission_form.study_id, s2['studyId'])
        self.assertEqual(submission_form.type, 'update_study')
        self.assertEqual(submission_form.submission.studyDesign['project']['name'], 'Project 2 (updated)')


    def test_strains(self):
        t1 = self.create_taxon(tax_names="R. intestinalis")
        t2 = self.create_taxon(tax_names="B. thetaiotaomicron")

        submission_form = SubmissionForm(db_session=self.db_session)
        self.assertEqual(submission_form.fetch_taxa(), [])

        submission_form.update_strains({'strains': [t1['tax_id']], 'new_strains': []})

        self.assertEqual(
            [t.tax_names for t in submission_form.fetch_taxa()],
            ['R. intestinalis'],
        )

        new_strains = [
            {'name': 'R. intestinalis 2',     'species': t1['tax_id']},
            {'name': 'B. thetaiotaomicron 2', 'species': t2['tax_id']},
            {'name': 'R. intestinalis 3',     'species': t1['tax_id']},
            {'name': 'Nonexistent',           'species': '999'},
        ]
        submission_form.update_strains({'strains': [], 'new_strains': new_strains})

        self.assertEqual(
            sorted([(s['name'], s['species_name']) for s in submission_form.fetch_new_strains()]),
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

        submission_form = SubmissionForm(db_session=self.db_session)
        self.assertEqual(submission_form.fetch_taxa(), [])

        study_design = submission_form.submission.studyDesign
        study_design['metabolites'] = [m1['chebi_id']]
        submission_form.update_study_design(study_design)

        self.assertEqual(
            [m.metabo_name for m in submission_form.fetch_metabolites()],
            ['glucose'],
        )

        study_design['metabolites'] = [m1['chebi_id'], m2['chebi_id']]
        submission_form.update_study_design(study_design)
        self.assertEqual(
            [m.metabo_name for m in submission_form.fetch_metabolites()],
            ['glucose', 'trehalose'],
        )


if __name__ == '__main__':
    unittest.main()

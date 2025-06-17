import tests.init  # noqa: F401

import unittest

from tests.database_test import DatabaseTest
from app.view.forms.submission_form import SubmissionForm


class TestSubmissionForm(DatabaseTest):
    def test_project_and_studies(self):
        p1 = self.create_project(projectName="Project 1")
        p2 = self.create_project(projectName="Project 2")
        s2 = self.create_study(projectUniqueID=p2.projectUniqueID)

        submission_form = SubmissionForm(db_session=self.db_session)
        self.assertEqual(submission_form.project_id, None)
        # No project, no study
        self.assertEqual(submission_form.type, 'new_project')

        submission_form.update_project({
            'project_uuid': p1.projectUniqueID,
            'project_name': 'Project 1 (updated)',
            'study_uuid':   '_new',
            'study_name':   'Study 1',
        })

        self.assertEqual(submission_form.project_id, p1.projectId)
        self.assertEqual(submission_form.type, 'new_study')
        self.assertEqual(submission_form.submission.studyDesign['project']['name'], 'Project 1 (updated)')

        submission_form.update_project({
            'project_uuid':        p2.projectUniqueID,
            'study_uuid':          s2.uuid,
            'project_name':        'Project 2 (updated)',
            'study_name':          'Study 2 (updated)',
            'project_description': 'Test',
            'study_description':   'Test',
        })

        self.assertEqual(submission_form.project_id, p2.projectId)
        self.assertEqual(submission_form.study_id, s2.studyId)
        self.assertEqual(submission_form.type, 'update_study')
        self.assertEqual(submission_form.submission.studyDesign['project']['name'], 'Project 2 (updated)')
        self.assertEqual(submission_form.submission.studyDesign['study']['name'], 'Study 2 (updated)')
        self.assertEqual(submission_form.submission.studyDesign['project']['description'], 'Test')
        self.assertEqual(submission_form.submission.studyDesign['study']['description'], 'Test')

    def test_project_and_study_uniqueness_validation(self):
        p1 = self.create_project(projectName="Project 1")
        self.create_study(studyName="Study 1", projectUniqueID=p1.projectUniqueID)

        submission_form = SubmissionForm(db_session=self.db_session)
        valid_params = {
            'project_uuid': '_new',
            'study_uuid':   '_new',
            'project_name': 'Project 1 (new)',
            'study_name':   'Study 1 (new)',
        }

        submission_form.update_project(valid_params)
        self.assertEqual(submission_form.errors, {})

        submission_form.update_project({**valid_params, 'project_name': 'Project 1'})
        self.assertTrue(submission_form.has_error('project_name'))
        self.assertEqual(submission_form.errors.get('project_name'), ["Project name is taken"])
        self.assertEqual(submission_form.error_messages(), ["Project name is taken"])

    def test_study_reuse(self):
        s1 = self.create_study()

        # First submission, creates project and study:
        submission = self.create_submission(
            studyUniqueID=s1.uuid,
            studyDesign={'timeUnits': "m"},
        )
        self.db_session.add(submission)
        self.db_session.flush()

        submission_form = SubmissionForm(db_session=self.db_session)
        submission_form.update_project({
            'project_uuid':     '_new',
            'project_name':     'Project 2',
            'study_uuid':       '_new',
            'study_name':       'Study 2',
            'reuse_study_uuid': s1.uuid,
        })

        s2_study_design = submission_form.submission.studyDesign
        self.assertEqual(s2_study_design['timeUnits'], 'm')

    def test_strains(self):
        t1 = self.create_taxon(name="R. intestinalis")
        t2 = self.create_taxon(name="B. thetaiotaomicron")

        submission_form = SubmissionForm(db_session=self.db_session)
        self.assertEqual(submission_form.fetch_taxa(), [])

        submission_form.update_strains({'strains': [t1.ncbiId], 'custom_strains': []})
        submission = submission_form.submission

        self.assertEqual(
            [t.name for t in submission_form.fetch_taxa()],
            ['R. intestinalis'],
        )

        custom_strains = [
            {'name': 'R. intestinalis 2',     'species': t1.ncbiId},
            {'name': 'B. thetaiotaomicron 2', 'species': t2.ncbiId},
            {'name': 'R. intestinalis 3',     'species': t1.ncbiId},
            {'name': 'Nonexistent',           'species': '999'},
        ]
        submission_form.update_strains({'strains': [], 'custom_strains': custom_strains})

        self.assertEqual(
            sorted([(s['name'], s['species_name']) for s in submission.studyDesign['custom_strains']]),
            sorted([
                ('R. intestinalis 2',     'R. intestinalis'),
                ('R. intestinalis 3',     'R. intestinalis'),
                ('B. thetaiotaomicron 2', 'B. thetaiotaomicron'),
                ('Nonexistent',           None),
            ]),
        )

    def test_metabolites(self):
        m1 = self.create_metabolite(name="glucose")
        m2 = self.create_metabolite(name="trehalose")

        submission_form = SubmissionForm(db_session=self.db_session)
        self.assertEqual(submission_form.fetch_taxa(), [])

        study_design = submission_form.submission.studyDesign
        study_design['techniques'] = [{'metaboliteIds': [m1.chebiId]}]
        submission_form.update_study_design(study_design)

        self.assertEqual(
            [m.name for m in submission_form.fetch_metabolites_for_technique(0)],
            ['glucose'],
        )

        study_design['techniques'] = [{'metaboliteIds': [m1.chebiId, m2.chebiId]}]
        submission_form.update_study_design(study_design)
        self.assertEqual(
            [m.name for m in submission_form.fetch_metabolites_for_technique(0)],
            ['glucose', 'trehalose'],
        )

    def test_technique_descriptions(self):
        submission_form = SubmissionForm(db_session=self.db_session)

        submission_form.update_study_design({
            'techniques': [
                {'type': 'fc',         'subjectType': 'bioreplicate'},
                {'type': 'od',         'subjectType': 'bioreplicate'},
                {'type': 'fc',         'subjectType': 'strain'},
                {'type': 'metabolite', 'subjectType': 'metabolite'},
            ]
        })
        self.assertEqual(
            [
                (subject_type, [t.type for t in techniques])
                for subject_type, techniques in submission_form.technique_descriptions()
            ],
            [
                ('Community-level', ['fc', 'od']),
                ('Strain-level',    ['fc']),
                ('Metabolite',      ['metabolite']),
            ]
        )

        # Sort them differently:
        submission_form.update_study_design({
            'techniques': [
                {'type': 'metabolite', 'subjectType': 'metabolite'},
                {'type': 'fc',         'subjectType': 'bioreplicate'},
                {'type': 'fc',         'subjectType': 'strain'},
                {'type': 'od',         'subjectType': 'bioreplicate'},
            ]
        })
        self.assertEqual(
            [
                (subject_type, [t.type for t in techniques])
                for subject_type, techniques in submission_form.technique_descriptions()
            ],
            [
                ('Community-level', ['fc', 'od']),
                ('Strain-level',    ['fc']),
                ('Metabolite',      ['metabolite']),
            ]
        )

        # Empty list results in empty description:
        submission_form.update_study_design({'techniques': []})
        self.assertEqual(list(submission_form.technique_descriptions()), [])


if __name__ == '__main__':
    unittest.main()

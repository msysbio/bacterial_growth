import tests.init  # noqa: F401

import unittest

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
            'project_uuid': p1['projectUniqueID'],
            'project_name': 'Project 1 (updated)',
            'study_uuid':   '_new',
            'study_name':   'Study 1',
        })

        self.assertEqual(submission_form.project_id, p1['projectId'])
        self.assertEqual(submission_form.type, 'new_study')
        self.assertEqual(submission_form.submission.studyDesign['project']['name'], 'Project 1 (updated)')

        submission_form.update_project({
            'project_uuid':        p2['projectUniqueID'],
            'study_uuid':          s2['studyUniqueID'],
            'project_name':        'Project 2 (updated)',
            'study_name':          'Study 2 (updated)',
            'project_description': 'Test',
            'study_description':   'Test',
        })

        self.assertEqual(submission_form.project_id, p2['projectId'])
        self.assertEqual(submission_form.study_id, s2['studyId'])
        self.assertEqual(submission_form.type, 'update_study')
        self.assertEqual(submission_form.submission.studyDesign['project']['name'], 'Project 2 (updated)')
        self.assertEqual(submission_form.submission.studyDesign['study']['name'], 'Study 2 (updated)')
        self.assertEqual(submission_form.submission.studyDesign['project']['description'], 'Test')
        self.assertEqual(submission_form.submission.studyDesign['study']['description'], 'Test')

    def test_project_and_study_uniqueness_validation(self):
        p1 = self.create_project(projectName="Project 1")
        self.create_study(studyName="Study 1", projectUniqueID=p1['projectUniqueID'])

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
        study_design['techniques'] = [{'metaboliteIds': [m1['chebi_id']]}]
        submission_form.update_study_design(study_design)

        self.assertEqual(
            [m.metabo_name for m in submission_form.fetch_metabolites_for_technique(0)],
            ['glucose'],
        )

        study_design['techniques'] = [{'metaboliteIds': [m1['chebi_id'], m2['chebi_id']]}]
        submission_form.update_study_design(study_design)
        self.assertEqual(
            [m.metabo_name for m in submission_form.fetch_metabolites_for_technique(0)],
            ['glucose', 'trehalose'],
        )

    def test_vessel_description(self):
        submission_form = SubmissionForm(db_session=self.db_session)

        submission_form.update_study_design({'vessel_type': 'bottles', 'bottle_count': 3})
        self.assertEqual(submission_form.vessel_description(), "3 bottles")

        submission_form.update_study_design({'vessel_type': 'agar_plates', 'plate_count': 5})
        self.assertEqual(submission_form.vessel_description(), "5 agar plates")

        submission_form.update_study_design({'vessel_type': 'well_plates', 'row_count': 5, 'column_count': 10})
        self.assertEqual(submission_form.vessel_description(), "5x10 well-plates")

        submission_form.update_study_design({'vessel_type': 'mini_react', 'row_count': 10, 'column_count': 12})
        self.assertEqual(submission_form.vessel_description(), "10x12 mini-bioreactors")

        # Invalid inputs:
        submission_form.update_study_design({'vessel_type': 'incorrect', 'row_count': 10, 'column_count': 12})
        self.assertEqual(submission_form.vessel_description(), "")
        submission_form.update_study_design({'vessel_type': 'bottles', 'bottle_count': None})
        self.assertEqual(submission_form.vessel_description(), "")
        submission_form.update_study_design({'vessel_type': 'well_plates', 'row_count': None})
        self.assertEqual(submission_form.vessel_description(), "")

    def test_timepoint_description(self):
        submission_form = SubmissionForm(db_session=self.db_session)

        submission_form.update_study_design({'timepoint_count': 7, 'time_units': 'h'})
        self.assertEqual(submission_form.timepoint_description(), "7 time points measured in hours")

        submission_form.update_study_design({'timepoint_count': 3, 'time_units': 'd'})
        self.assertEqual(submission_form.timepoint_description(), "3 time points measured in days")

        submission_form.update_study_design({'timepoint_count': 13, 'time_units': 'm'})
        self.assertEqual(submission_form.timepoint_description(), "13 time points measured in minutes")

        submission_form.update_study_design({'timepoint_count': 80, 'time_units': 's'})
        self.assertEqual(submission_form.timepoint_description(), "80 time points measured in seconds")

        # Invalid inputs:
        submission_form.update_study_design({'timepoint_count': 0, 'time_units': 's'})
        self.assertEqual(submission_form.timepoint_description(), "")
        submission_form.update_study_design({'timepoint_count': 10, 'time_units': 'unknown'})
        self.assertEqual(submission_form.timepoint_description(), "")

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
                ('Sample-level', ['fc', 'od']),
                ('Strain-level', ['fc']),
                ('Metabolite',   ['metabolite']),
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
                ('Sample-level', ['fc', 'od']),
                ('Strain-level', ['fc']),
                ('Metabolite',   ['metabolite']),
            ]
        )

        # Empty list results in empty description:
        submission_form.update_study_design({'techniques': []})
        self.assertEqual(list(submission_form.technique_descriptions()), [])


if __name__ == '__main__':
    unittest.main()

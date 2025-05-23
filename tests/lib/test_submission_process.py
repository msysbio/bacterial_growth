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
    _save_experiments,
    _save_measurement_techniques,
    _create_average_measurements,
)
from tests.database_test import DatabaseTest


class TestSubmissionProcess(DatabaseTest):
    def setUp(self):
        super().setUp()

        self.submission = self.create_submission(
            studyDesign={
                'project': {'name': 'Test project'},
                'study':   {'name': 'Test study'}
            }
        )

    def test_project_and_study_creation(self):
        submission_form = SubmissionForm(submission_id=self.submission.id, db_session=self.db_session)

        # Creating a new project and study:
        project = self.db_session.get(Project, self.submission.projectUniqueID)
        study   = self.db_session.get(Study,   self.submission.studyUniqueID)
        self.assertIsNone(project)
        self.assertIsNone(study)

        _save_project(self.db_session, submission_form)
        _save_study(self.db_session, submission_form)
        self.db_session.flush()

        project = self.db_session.get(Project, self.submission.projectUniqueID)
        study   = self.db_session.get(Study,   self.submission.studyUniqueID)
        self.assertIsNotNone(project)
        self.assertIsNotNone(study)
        self.assertEqual(project.name, 'Test project')
        self.assertEqual(study.name, 'Test study')

        # Updating the existing project and study:
        submission_form.update_project({
            'project_uuid': self.submission.projectUniqueID,
            'study_uuid':   self.submission.studyUniqueID,
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
        submission_form = SubmissionForm(submission_id=self.submission.id, db_session=self.db_session)

        with freeze_time(datetime.now(UTC)) as frozen_time:
            _save_project(self.db_session, submission_form)
            _save_study(self.db_session, submission_form)
            self.db_session.flush()

            study = self.db_session.get(Study, self.submission.studyUniqueID)

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
        submission_form = SubmissionForm(submission_id=self.submission.id, db_session=self.db_session)
        submission_form.update_study_design({
            'compartments': [{
                'name': 'WC',
                'mediumName': 'Wilkins-Chalgren',
            }, {
                'name': 'Mucin',
                'mediumName': 'Mucin',
            }]
        })
        submission_form.save()

        # Creating compartments defined by the self.submission
        study        = _save_study(self.db_session, submission_form)
        compartments = _save_compartments(self.db_session, submission_form, study)

        self.db_session.flush()

        self.assertEqual(['WC', 'Mucin'], [c.name for c in compartments])
        self.assertEqual(compartments, study.compartments)
        self.assertEqual(2, self.db_session.scalar(sql.func.count(Compartment.id)))

        # Remove all compartments
        self.submission.studyDesign['compartments'] = []
        compartments = _save_compartments(self.db_session, submission_form, study)

        self.db_session.flush()
        self.db_session.refresh(study)

        self.assertEqual([], [c.name for c in compartments])
        self.assertEqual(compartments, study.compartments)
        self.assertEqual(0, self.db_session.scalar(sql.func.count(Compartment.id)))

    def test_community_creation(self):
        t_ri = self.create_taxon(name='Roseburia intestinalis')
        t_bh = self.create_taxon(name='Blautia hydrogenotrophica')

        submission_form = SubmissionForm(submission_id=self.submission.id, db_session=self.db_session)
        submission_form.update_study_design({
            'project': {'name': 'Test project'},
            'study':   {'name': 'Test study'},

            'new_strains': [{
                'name': 'Custom strain',
                'description': 'test',
                'species': t_ri.ncbiId,
            }],

            'communities': [{
                'name': 'Full',
                'strainIdentifiers': [
                    f"existing|{t_ri.ncbiId}",
                    f"existing|{t_bh.ncbiId}",
                    'custom|Custom strain',
                ],
            }, {
                'name': 'RI',
                'strainIdentifiers': [f"existing|{t_ri.ncbiId}"]
            }, {
                'name': 'Blank',
                'strainIdentifiers': [],
            }]
        })

        # Creating compartments defined by the submission
        study       = _save_study(self.db_session, submission_form)
        communities = _save_communities(self.db_session, submission_form, study, user_uuid='user1')

        self.db_session.flush()

        self.assertEqual(['Full', 'RI', 'Blank'], [c.name for c in communities])
        self.assertEqual(communities, study.communities)
        self.assertEqual(3, self.db_session.scalar(sql.func.count(Community.id)))

        # Check existence of strains:
        s_ri     = self.db_session.scalar(sql.select(Strain).where(Strain.NCBId == t_ri.ncbiId))
        s_bh     = self.db_session.scalar(sql.select(Strain).where(Strain.NCBId == t_bh.ncbiId))
        s_custom = self.db_session.scalar(sql.select(Strain).where(Strain.name == 'Custom strain'))

        c_full, c_ri, c_blank = communities
        self.assertEqual(set(c_full.strainIds), {s_ri.id, s_bh.id, s_custom.id})

        # Remove all communities
        self.submission.studyDesign['communities'] = []
        communities = _save_communities(self.db_session, submission_form, study, user_uuid='user1')

        self.db_session.flush()
        self.db_session.refresh(study)

        self.assertEqual([], [c.name for c in communities])
        self.assertEqual(communities, study.communities)
        self.assertEqual(0, self.db_session.scalar(sql.func.count(Community.id)))

    def test_experiment_creation(self):
        t_ri = self.create_taxon(name='Roseburia intestinalis')

        submission_form = SubmissionForm(submission_id=self.submission.id, db_session=self.db_session)
        submission_form.update_study_design({
            'compartments': [
                {'name': 'WC',    'mediumName': 'WC'},
                {'name': 'MUCIN', 'mediumName': 'WC'}
            ],
            'communities': [
                {'name': 'RI', 'strainIdentifiers': [f"existing|{t_ri.ncbiId}"]},
            ],

            'experiments': [{
                'name': 'RI',
                'description': 'RI experiment',
                'cultivationMode': 'batch',
                'communityName': 'RI',
                'compartmentNames': ['WC', 'MUCIN'],
                'bioreplicates': [
                    {'name': 'RI_1'},
                    {'name': 'RI_2'},
                    {'name': 'RI_3'},
                ],
                'perturbations': [{
                    'description': 'Change everything',
                    'startTimepoint': 3,
                    'removedCompartmentName': 'MUCIN',
                    'addedCompartmentName': '',
                    'newCommunityName': 'RI',
                    'oldCommunityName': '',
                }]
            }]
        })

        # Create dependencies
        study        = _save_study(self.db_session, submission_form)
        communities  = _save_communities(self.db_session, submission_form, study, user_uuid='user1')
        compartments = _save_compartments(self.db_session, submission_form, study)

        experiments = _save_experiments(self.db_session, submission_form, study)

        self.db_session.flush()

        self.assertEqual(len(experiments), 1)
        self.assertEqual(experiments, study.experiments)

        experiment = experiments[0]

        self.assertEqual(experiment.community, communities[0])
        self.assertEqual(len(experiment.compartments), 2)
        self.assertEqual(experiment.compartments, compartments)

        self.assertEqual(len(experiment.perturbations), 1)
        self.assertEqual(experiment.perturbations, study.perturbations)
        self.assertEqual(experiment.perturbations[0].newCommunityId, communities[0].id)

        self.assertEqual(len(experiment.bioreplicates), 3)
        self.assertEqual(len(study.bioreplicates), 3)
        self.assertEqual({'RI_1', 'RI_2', 'RI_3'}, {b.name for b in study.bioreplicates})

    def test_measurement_technique_creation(self):
        m1 = self.create_metabolite(name='pyruvate')
        m2 = self.create_metabolite(name='butyrate')

        submission_form = SubmissionForm(submission_id=self.submission.id, db_session=self.db_session)
        submission_form.update_study_design({
            'techniques': [{
                'type': 'od',
                'units': '',
                'includeStd': False,
                'subjectType': 'bioreplicate',
                'metaboliteIds': [],
            }, {
                'type': 'fc',
                'units': 'Cells/mL',
                'includeStd': True,
                'subjectType': 'strain',
                'metaboliteIds': [],
            }, {
                'type': 'metabolite',
                'units': 'mM',
                'includeStd': False,
                'subjectType': 'strain',
                'metaboliteIds': [m1.chebiId, m2.chebiId],
            }]
        })
        submission_form.save()

        study = _save_study(self.db_session, submission_form)

        techniques = _save_measurement_techniques(self.db_session, submission_form, study)
        self.db_session.flush()

        self.assertEqual(len(techniques), 3)
        self.assertEqual(techniques, study.measurementTechniques)
        self.assertEqual({m.name for m in study.metabolites}, {'pyruvate', 'butyrate'})

    def test_average_measurement_creation(self):
        study      = self.create_study()
        experiment = self.create_experiment(name="e1", studyId=study.publicId)

        b1 = self.create_bioreplicate(name="b1", studyId=study.publicId, experimentId=experiment.id)
        b2 = self.create_bioreplicate(name="b2", studyId=study.publicId, experimentId=experiment.id)

        c1 = self.create_compartment(studyId=study.publicId)
        study.experiments[0].compartments = [c1]

        mt = self.create_measurement_technique(subjectType='bioreplicate', studyUniqueID=study.uuid)

        mc1 = self.create_measurement_context(
            subjectId=b1.id,
            subjectType='bioreplicate',
            bioreplicateId=b1.id,
            techniqueId=mt.id,
            compartmentId=c1.id,
            studyId=study.publicId,
        )
        for i, value in enumerate([10, 20, 30]):
            self.create_measurement(timeInSeconds=i, value=value, contextId=mc1.id)

        mc2 = self.create_measurement_context(
            subjectId=b2.id,
            subjectType='bioreplicate',
            bioreplicateId=b1.id,
            techniqueId=mt.id,
            compartmentId=c1.id,
            studyId=study.publicId,
        )
        for i, value in enumerate([20, 40, 60]):
            self.create_measurement(timeInSeconds=i, value=value, contextId=mc2.id)

        _create_average_measurements(self.db_session, study, experiment)
        self.db_session.flush()

        self.assertEqual({b.name for b in study.bioreplicates}, {"b1", "b2", "Average(e1)"})

        average_bioreplicate = next(b for b in study.bioreplicates if b.name == "Average(e1)")
        self.assertEqual(average_bioreplicate.calculationType, 'average')
        self.assertEqual([int(m.value) for m in average_bioreplicate.measurements], [15, 30, 45])


if __name__ == '__main__':
    unittest.main()

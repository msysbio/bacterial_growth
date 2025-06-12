import itertools
from uuid import uuid4

import sqlalchemy as sql
from sqlalchemy.orm.attributes import flag_modified

from app.model.orm import (
    Taxon,
    Metabolite,
    Project,
    Study,
    Submission,
)

# The structure of a Submission's `studyDesign` field. Any parameters given to
# the form will be merged with this as a default. Changing the structure here
# will allow stored submissions to be reused and made compatible with the new
# structure.
#
# When the `submission.studyDesign` is modified, we need to use `flag_modified`
# to tell the ORM to persist the field.
#
DEFAULT_STUDY_DESIGN = {
    'project': {'name': None, 'description': None},
    'study':   {'name': None, 'description': None, 'url': None},

    'timeUnits': None,

    'strains':        [],
    'custom_strains': [],
    'techniques':     [],
    'compartments':   [],
    'communities':    [],
    'experiments':    [],
}


class SubmissionForm:
    def __init__(self, submission_id=None, step=0, db_session=None, user_uuid=None):
        self.step       = step
        self.db_session = db_session
        self.errors     = []

        # Load submission object
        self.submission = None
        if submission_id is not None:
            self.submission = self.db_session.get(Submission, submission_id)

        if self.submission is not None:
            self.submission.studyDesign = {
                **DEFAULT_STUDY_DESIGN,
                **self.submission.studyDesign,
            }
        else:
            self.submission = Submission(
                projectUniqueID=None,
                studyUniqueID=None,
                userUniqueID=user_uuid,
                studyDesign=DEFAULT_STUDY_DESIGN,
            )

        # Check for an existing project/study and set the submission "type" accordingly:
        self.project_id = self._find_project_id()
        self.study_id   = self._find_study_id()
        self.type       = self._determine_project_type()

    def update_project(self, data):
        # Update IDs:
        if data['project_uuid'] == '_new':
            self.submission.projectUniqueID = str(uuid4())
        else:
            self.submission.projectUniqueID = data['project_uuid']

        if data['study_uuid'] == '_new':
            self.submission.studyUniqueID = str(uuid4())
        else:
            self.submission.studyUniqueID = data['study_uuid']

        # If study to reuse has been given, copy its last submission's study
        # design:
        if data.get('reuse_study_uuid', '') != '':
            previous_submission = self.db_session.scalars(
                sql.select(Submission)
                .where(Submission.studyUniqueID == data['reuse_study_uuid'])
                .order_by(Submission.updatedAt.desc())
                .limit(1)
            ).one_or_none()

            if previous_submission:
                self.submission.studyDesign = previous_submission.studyDesign

        # Update text fields:
        self.submission.studyDesign['project'] = {
            'name':        data['project_name'],
            'description': data.get('project_description', ''),
        }
        self.submission.studyDesign['study'] = {
            'name':        data['study_name'],
            'description': data.get('study_description', ''),
            'url':         data.get('study_url', ''),
        }
        flag_modified(self.submission, 'studyDesign')

        # Validate uniqueness:
        self._validate_unique_project_names()

        # Check whether projects exist:
        self.project_id = self._find_project_id()
        self.study_id   = self._find_study_id()
        self.type       = self._determine_project_type()

    def update_strains(self, data):
        # Existing strains
        self.submission.studyDesign['strains'] = data['strains']

        # Add parent species name to custom strain data:
        for strain in data['custom_strains']:
            if 'species_name' in strain:
                continue

            strain['species_name'] = self.db_session.scalars(
                sql.select(Taxon.name)
                .where(Taxon.ncbiId == strain['species'])
                .limit(1)
            ).one_or_none()

        # Save new strains
        self.submission.studyDesign['custom_strains'] = data['custom_strains']

        # Clean up strain names:
        for strain_data in self.submission.studyDesign['custom_strains']:
            strain_data['name'] = strain_data['name'].strip()

        flag_modified(self.submission, 'studyDesign')

    def update_study_design(self, data):
        study_design = {**self.submission.studyDesign, **data}
        if 'csrf_token' in study_design:
            del study_design['csrf_token']

        self.submission.studyDesign = study_design
        flag_modified(self.submission, 'studyDesign')

    def fetch_taxa(self):
        strains = self.submission.studyDesign['strains']

        return self.db_session.scalars(
            sql.select(Taxon)
            .where(Taxon.ncbiId.in_(strains))
        ).all()

    def fetch_metabolites_for_technique(self, technique_index=None):
        if technique_index is None:
            # In a new form, we don't have any metabolites to list
            return []

        techniques = self.submission.studyDesign['techniques']
        metabolites = techniques[technique_index]['metaboliteIds']

        return self.db_session.scalars(
            sql.select(Metabolite)
            .where(Metabolite.chebiId.in_(metabolites))
        ).all()

    def fetch_all_metabolites(self):
        ids = [
            m_id
            for t in self.submission.studyDesign['techniques']
            for m_id in t['metaboliteIds']
        ]

        return self.db_session.scalars(
            sql.select(Metabolite)
            .where(Metabolite.chebiId.in_(ids))
        ).all()

    def save(self):
        self.db_session.add(self.submission)
        self.db_session.commit()

        return self.submission.id

    def has_error(self, key):
        return key in self.errors

    def error_messages(self):
        # Flatten messages per property:
        return list(itertools.chain.from_iterable(self.errors.values()))

    def technique_descriptions(self):
        ordering = ('bioreplicate', 'strain', 'metabolite')
        techniques = sorted(self.submission.build_techniques(), key=lambda t: ordering.index(t.subjectType))

        for (subject_type, techniques) in itertools.groupby(techniques, lambda t: t.subjectType):
            match subject_type:
                case 'bioreplicate': type = 'Community-level'
                case 'strain':       type = 'Strain-level'
                case 'metabolite':   type = 'Metabolite'

            yield (type, list(techniques))

    def html_step_classes(self, target_step):
        if self.step < target_step:
            return 'disabled'
        elif self.step == target_step:
            return 'active'
        else:
            return ''

    def has_valid_project_data(self):
        if self.submission.studyDesign['project']['name'] is None:
            return False
        return self._validate_unique_project_names()

    def has_valid_study_data(self):
        return self.submission.studyDesign['study']['name'] is not None

    def _find_project_id(self):
        if self.submission.projectUniqueID is None:
            return None

        return self.db_session.scalars(
            sql.select(Project.projectId)
            .where(Project.projectUniqueID == self.submission.projectUniqueID)
        ).one_or_none()

    def _find_study_id(self):
        if self.submission.studyUniqueID is None:
            return None

        return self.db_session.scalars(
            sql.select(Study.studyId)
            .where(Study.studyUniqueID == self.submission.studyUniqueID)
        ).one_or_none()

    def _determine_project_type(self):
        if self.project_id and self.study_id:
            return 'update_study'
        elif self.project_id:
            return 'new_study'
        else:
            return 'new_project'

    def _validate_unique_project_names(self):
        self.errors = {}

        project_name = self.submission.studyDesign['project']['name']

        if len(project_name) > 0:
            project_exists = self.db_session.query(
                sql.exists()
                .where(
                    Project.projectName == project_name,
                    Project.projectUniqueID != self.submission.projectUniqueID
                )
            ).scalar()

            if project_exists:
                self.errors['project_name'] = ["Project name is taken"]

        return len(self.errors) == 0

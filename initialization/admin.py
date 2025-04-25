import re

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy.orm import configure_mappers

from db import get_session
from models import (
    Calculation,
    CalculationTechnique,
    Measurement,
    MeasurementTechnique,
    Metabolite,
    ProjectUser,
    Study,
    StudyUser,
    Submission,
    Taxon,
)


class AppView(ModelView):
    can_export = True
    can_view_details = True

    def _prettify_name(self, name):
        return re.sub(r'([a-z])([A-Z])', r'\1 \2', name).title()


def init_admin(app):
    configure_mappers()

    admin = Admin(app, name='μGrowthDB admin', template_mode='bootstrap4')

    # TODO (2025-04-25) This session is not reloaded
    db_session = get_session()

    class StudyView(AppView):
        column_searchable_list = ['studyName', 'studyDescription']
    admin.add_view(StudyView(Study, db_session, category="Studies"))

    admin.add_view(AppView(Submission, db_session, category="Studies"))

    admin.add_view(AppView(MeasurementTechnique, db_session, category="Measurements"))
    admin.add_view(AppView(Measurement, db_session, category="Measurements"))
    admin.add_view(AppView(CalculationTechnique, db_session, category="Measurements"))
    admin.add_view(AppView(Calculation, db_session, category="Measurements"))

    admin.add_view(AppView(Metabolite, db_session, category="External data"))
    admin.add_view(AppView(Taxon, db_session, category="External data"))

    admin.add_view(AppView(StudyUser, db_session, category="Users"))
    admin.add_view(AppView(ProjectUser, db_session, category="Users"))

    return app

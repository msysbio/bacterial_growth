from flask import g
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from db import get_session
from models import (
    Study,
    Submission,
    MeasurementTechnique,
    Measurement,
    Metabolite,
    Taxon,
)

class AppView(ModelView):
    can_export = True
    can_view_details = True

def init_admin(app):
    admin = Admin(app, name='μGrowthDB admin', template_mode='bootstrap4')

    db_session = get_session()

    class StudyView(AppView):
        column_searchable_list = ['studyName', 'studyDescription']
    admin.add_view(StudyView(Study, db_session, category="Studies"))

    admin.add_view(AppView(Submission, db_session, category="Studies"))

    admin.add_view(AppView(MeasurementTechnique, db_session, category="Measurements"))
    admin.add_view(AppView(Measurement, db_session, category="Measurements"))

    admin.add_view(AppView(Metabolite, db_session, category="External data"))
    admin.add_view(AppView(Taxon, db_session, category="External data"))

    return app

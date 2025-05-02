import re
import json

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy.orm import configure_mappers
from markupsafe import Markup

from db import FLASK_DB
from models.orm_base import OrmBase
from models import (
    Calculation,
    CalculationTechnique,
    Measurement,
    MeasurementTechnique,
    Metabolite,
    ProjectUser,
    Strain,
    Study,
    StudyUser,
    Submission,
    Taxon,
)


def json_formatter(_view, data, _name):
    return Markup(f"<pre>{json.dumps(data, indent=2)}</pre>")


def record_formatter(_view, record, _name):
    if hasattr(record, 'publicId'):
        return record.publicId
    elif hasattr(record, 'name'):
        return record.name
    else:
        return str(record)


class AppView(ModelView):
    can_export = True
    can_view_details = True

    def _prettify_name(self, name):
        return re.sub(r'([a-z])([A-Z])', r'\1 \2', name).title()

    column_type_formatters = {
        dict: json_formatter,
        OrmBase: record_formatter,
    }


def init_admin(app):
    configure_mappers()

    admin = Admin(app, name='μGrowthDB admin', template_mode='bootstrap4')

    db_session = FLASK_DB.session

    class StudyView(AppView):
        column_searchable_list = ['studyName', 'studyDescription']

    admin.add_view(StudyView(Study,    db_session, category="Studies"))
    admin.add_view(AppView(Submission, db_session, category="Studies"))
    admin.add_view(AppView(Strain,     db_session, category="Studies"))

    admin.add_view(AppView(MeasurementTechnique, db_session, category="Measurements"))
    admin.add_view(AppView(Measurement,          db_session, category="Measurements"))
    admin.add_view(AppView(CalculationTechnique, db_session, category="Measurements"))
    admin.add_view(AppView(Calculation,          db_session, category="Measurements"))

    admin.add_view(AppView(Metabolite, db_session, category="External data"))
    admin.add_view(AppView(Taxon,      db_session, category="External data"))

    admin.add_view(AppView(StudyUser,   db_session, category="Users"))
    admin.add_view(AppView(ProjectUser, db_session, category="Users"))

    return app

import io
from datetime import datetime, timezone

import simplejson as json
from wtforms import fields
from werkzeug.exceptions import NotFound
from sqlalchemy.orm import configure_mappers
from markupsafe import Markup
from flask import (
    g,
    send_file,
    request,
)
from flask_admin import Admin, form, AdminIndexView, expose
from flask_admin.model.form import converts
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.form import AdminModelConverter
from flask_admin._compat import as_unicode
from flask_admin.model.template import EndpointLinkRowAction

from db import FLASK_DB
from app.model.orm.orm_base import OrmBase
from app.model.orm import (
    Bioreplicate,
    Community,
    Compartment,
    ExcelFile,
    Experiment,
    ExperimentCompartment,
    Measurement,
    MeasurementContext,
    MeasurementTechnique,
    Metabolite,
    ModelingRequest,
    ModelingResult,
    Perturbation,
    Project,
    ProjectUser,
    Strain,
    Study,
    StudyMetabolite,
    StudyUser,
    Submission,
    Taxon,
    User,
)
from app.model.lib.util import humanize_camelcased_string


def json_formatter(_view, data, _name):
    return Markup(f"<pre>{json.dumps(data, indent=2, use_decimal=True)}</pre>")


def record_formatter(_view, record, *args):
    if hasattr(record, 'publicId'):
        return record.publicId
    elif hasattr(record, 'name'):
        return record.name
    else:
        return str(record)


FORMATTERS = {
    dict: json_formatter,
    OrmBase: record_formatter,
}


class AppJSONField(fields.TextAreaField):
    """
    Copied from Flask-admin to replace `json` with `simplejson` with `use_decimal=True`
    """
    def _value(self):
        if self.raw_data:
            return self.raw_data[0]
        elif self.data:
            # prevent utf8 characters from being converted to ascii
            return as_unicode(json.dumps(self.data, use_decimal=True, ensure_ascii=False))
        else:
            return '{}'

    def process_formdata(self, valuelist):
        if valuelist:
            value = valuelist[0]

            # allow saving blank field as None
            if not value:
                self.data = None
                return

            try:
                self.data = json.loads(valuelist[0], use_decimal=True)
            except ValueError:
                raise ValueError(self.gettext('Invalid JSON'))


class AppModelConverter(AdminModelConverter):
    @converts('JSON')
    def convert_JSON(self, field_args, **extra):
        return AppJSONField(**field_args)

    @converts('UtcDateTime')
    def convert_datetime(self, field_args, **extra):
        return AppDateTimeField(**field_args, default=datetime.utcnow)


class AppDateTimeField(form.DateTimeField):
    def process_formdata(self, valuelist):
        if not valuelist:
            return

        date_str = " ".join(valuelist)
        for format in self.strptime_format:
            try:
                self.data = datetime.strptime(date_str, format).replace(tzinfo=timezone.utc)
                return
            except ValueError:
                self.data = None

        raise ValueError(self.gettext("Not a valid datetime value."))


class AppAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not g.current_user or not g.current_user.isAdmin:
            raise NotFound()
        return super(AppAdminIndexView, self).index()


class AppView(ModelView):
    can_export       = True
    can_view_details = True

    model_form_converter = AppModelConverter

    def prettify_name(self, name):
        return humanize_camelcased_string(name).title()

    column_type_formatters        = FORMATTERS
    column_type_formatters_export = FORMATTERS
    column_type_formatters_detail = FORMATTERS

    def is_accessible(self):
        return g.current_user and g.current_user.isAdmin

    def inaccessible_callback(self, name, **kwargs):
        raise NotFound()


def init_admin(app):
    configure_mappers()

    admin = Admin(
        app,
        name='μGrowthDB admin',
        index_view=AppAdminIndexView(),
    )

    db_session = FLASK_DB.session

    class StudyView(AppView):
        column_searchable_list = ['studyName']
        column_exclude_list = ['studyDescription']
        form_excluded_columns = ['measurements', 'measurementContexts', 'measurementTechniques']

    class SubmissionView(AppView):
        column_exclude_list = ['studyDesign', 'dataFile']
        form_excluded_columns = ['project', 'study']

    class ExcelFileView(AppView):
        column_exclude_list         = ['content']
        column_details_exclude_list = ['content']

        can_edit   = False
        can_create = False
        can_export = False

        column_extra_row_actions = [
            EndpointLinkRowAction("fa fa-download", ".download_view"),
        ]

        @expose("/download", methods=("GET",))
        def download_view(self):
            file = g.db_session.get(ExcelFile, request.args['id'])

            return send_file(
                io.BytesIO(file.content),
                as_attachment=True,
                download_name=file.filename
            )

    admin.add_view(AppView(Project,           db_session, category="Studies"))
    admin.add_view(StudyView(Study,           db_session, category="Studies"))
    admin.add_view(SubmissionView(Submission, db_session, category="Studies"))
    admin.add_view(AppView(Strain,            db_session, category="Studies"))
    admin.add_view(AppView(StudyMetabolite,   db_session, category="Studies"))
    admin.add_view(ExcelFileView(ExcelFile,   db_session, category="Studies"))

    admin.add_view(AppView(Experiment,            db_session, category="Experiments"))
    admin.add_view(AppView(ExperimentCompartment, db_session, category="Experiments"))
    admin.add_view(AppView(Compartment,           db_session, category="Experiments"))
    admin.add_view(AppView(Bioreplicate,          db_session, category="Experiments"))
    admin.add_view(AppView(Community,             db_session, category="Experiments"))
    admin.add_view(AppView(Perturbation,          db_session, category="Experiments"))

    admin.add_view(AppView(MeasurementTechnique, db_session, category="Measurements"))
    admin.add_view(AppView(MeasurementContext,   db_session, category="Measurements"))
    admin.add_view(AppView(Measurement,          db_session, category="Measurements"))
    admin.add_view(AppView(ModelingRequest,      db_session, category="Measurements"))
    admin.add_view(AppView(ModelingResult,       db_session, category="Measurements"))

    class MetaboliteView(AppView):
        column_searchable_list = ['name']
        form_excluded_columns = ['studyMetabolites']

    class TaxonView(AppView):
        column_searchable_list = ['name']

    admin.add_view(MetaboliteView(Metabolite, db_session, category="External data"))
    admin.add_view(TaxonView(Taxon,           db_session, category="External data"))

    class UserView(AppView):
        form_excluded_columns = ['createdAt', 'updatedAt', 'lastLoginAt']

    admin.add_view(UserView(User,       db_session, category="Users"))
    admin.add_view(AppView(StudyUser,   db_session, category="Users"))
    admin.add_view(AppView(ProjectUser, db_session, category="Users"))

    return app

from datetime import datetime
from flask import render_template
import sqlalchemy as sql

from flask_app.app.forms.search_form import SearchForm
from flask_app.app.db import get_connection

from src.db_functions import dynamical_query


def index_page():
    return render_template("pages/index.html")


def search_page():
    form = SearchForm()

    if form.validate_on_submit():
        query = dynamical_query([{ 'option': form.option.data, 'value': form.value.data }])
        with get_connection() as conn:
            studies = [studyId for (studyId,) in conn.execute(sql.text(query))]
            print(result)
            return render_template("pages/search.html", form=form)

    return render_template("pages/search.html", form=form)


def dashboard_page():
    return render_template("pages/dashboard.html")


def upload_page():
    return render_template("pages/upload.html")


def help_page():
    return render_template("pages/help.html")


def about_page():
    return render_template("pages/about.html")

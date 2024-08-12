from datetime import datetime
from flask import render_template


def index_page():
    return render_template("pages/index.html")


def search_page():
    return render_template("pages/search.html")


def dashboard_page():
    return render_template("pages/dashboard.html")


def upload_page():
    return render_template("pages/upload.html")


def help_page():
    return render_template("pages/help.html")


def about_page():
    return render_template("pages/about.html")

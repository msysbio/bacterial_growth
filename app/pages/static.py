"""
Static pages: home, about
"""

from flask import render_template


def static_home_page():
    return render_template("pages/static/home.html")


def static_about_page():
    return render_template("pages/static/about.html")

"""
Static pages: home, about, help
"""

from flask import render_template


def home():
    return render_template("pages/static/home.html")


def about():
    return render_template("pages/static/about.html")


def help():
    return render_template("pages/static/help.html")

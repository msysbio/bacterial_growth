from datetime import datetime
from flask import render_template


def index():
    return render_template("index.html")

def about():
    return render_template("about.html")

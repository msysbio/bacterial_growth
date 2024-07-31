from datetime import datetime
from flask import render_template


def index():
    today = datetime.today()
    day_name = today.strftime("%A")

    return render_template("index.html", day_name=day_name)

from flask import render_template


def dashboard_index_page():
    return render_template("pages/dashboard.html")

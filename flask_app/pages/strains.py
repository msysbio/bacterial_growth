from flask import render_template
import sqlalchemy as sql

from flask_app.db import get_connection


def strain_show_page(id):
    with get_connection() as conn:
        query = "SELECT * FROM Strains WHERE strainId = :id LIMIT 1"
        strain = conn.execute(sql.text(query), {'id': id}).one()._asdict()

        query = "SELECT studyId, studyName FROM Study WHERE studyId = :studyId LIMIT 1"
        study = conn.execute(sql.text(query), {'studyId': strain['studyId']}).one()._asdict()

        return render_template("pages/strains/show.html", strain=strain, study=study)

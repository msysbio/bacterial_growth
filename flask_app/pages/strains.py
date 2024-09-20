import json

from flask import render_template, request
import sqlalchemy as sql

from flask_app.db import get_connection


def strain_show_page(id):
    with get_connection() as conn:
        query = "SELECT * FROM Strains WHERE strainId = :id LIMIT 1"
        strain = conn.execute(sql.text(query), {'id': id}).one()._asdict()

        query = "SELECT studyId, studyName FROM Study WHERE studyId = :studyId LIMIT 1"
        study = conn.execute(sql.text(query), {'studyId': strain['studyId']}).one()._asdict()

        return render_template("pages/strains/show.html", strain=strain, study=study)

def strain_completion_json():
    with get_connection() as conn:
        term = request.args.get('term', '')
        query = """
            SELECT
                tax_id AS id,
                tax_names AS text
            FROM Taxa
            WHERE LOWER(tax_names) LIKE LOWER(:q)
            ORDER BY tax_names ASC
        """
        results = conn.execute(sql.text(query), {'q': f'{term}%'}).all()
        results = [row._asdict() for row in results]

        return json.dumps({ 'results': results })

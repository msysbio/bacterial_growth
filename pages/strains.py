import json

from flask import render_template, request
import sqlalchemy as sql

from db import get_connection
from models.taxon import Taxon


def strain_show_page(id):
    with get_connection() as conn:
        query = "SELECT * FROM Strains WHERE strainId = :id LIMIT 1"
        strain = conn.execute(sql.text(query), {'id': id}).one()._asdict()

        query = "SELECT studyId, studyName FROM Study WHERE studyId = :studyId LIMIT 1"
        study = conn.execute(sql.text(query), {'studyId': strain['studyId']}).one()._asdict()

        return render_template("pages/strains/show.html", strain=strain, study=study)


def taxa_completion_json():
    term     = request.args.get('term', '').lower()
    page     = int(request.args.get('page', '1'))
    per_page = 10

    # TODO (2024-09-21) Extract to model and test

    with get_connection() as conn:
        results, has_more = Taxon.search_by_name(conn, term, page, per_page)

        return json.dumps({
            'results': results,
            'pagination': {'more': has_more},
        })

import re
import json

from flask import render_template, request
import sqlalchemy as sql

from db import get_connection
from app.model.orm import Metabolite


def metabolite_show_page(chebiId):
    with get_connection() as conn:
        query = "SELECT * FROM Metabolites WHERE chebiId = :chebi_id LIMIT 1"
        metabolite = conn.execute(sql.text(query), {'chebi_id': chebiId}).one()._asdict()
        numeric_id = re.sub(r'^CHEBI:', '', chebiId)

        return render_template(
            "pages/metabolites/show.html",
            metabolite=metabolite,
            chebi_id=chebiId,
            numeric_id=numeric_id
        )


def metabolites_completion_json():
    term     = request.args.get('term', '')
    page     = int(request.args.get('page', '1'))
    per_page = 10

    with get_connection() as conn:
        results, has_more = Metabolite.search_by_name(conn, term, page, per_page)

        return json.dumps({
            'results': results,
            'pagination': {'more': has_more},
        })

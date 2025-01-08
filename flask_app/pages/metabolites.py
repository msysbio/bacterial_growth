import re
import json

from flask import render_template, request
import sqlalchemy as sql

from flask_app.db import get_connection


def metabolite_show_page(chebi_id):
    with get_connection() as conn:
        query = "SELECT * FROM Metabolites WHERE chebi_id = :chebi_id LIMIT 1"
        metabolite = conn.execute(sql.text(query), {'chebi_id': chebi_id}).one()._asdict()
        numeric_id = re.sub(r'^CHEBI:', '', chebi_id)

        return render_template(
            "pages/metabolites/show.html",
            metabolite=metabolite,
            chebi_id=chebi_id,
            numeric_id=numeric_id
        )


# TODO (2024-09-26) Duplicates taxa completion a lot, try to make completion
# model generic
def metabolites_completion_json():
    term     = request.args.get('term', '').lower()
    page     = int(request.args.get('page', '1'))
    per_page = 10

    # TODO (2024-09-21) Extract to model and test

    with get_connection() as conn:
        query = """
            SELECT
                chebi_id AS id,
                metabo_name AS text
            FROM Metabolites
            WHERE LOWER(metabo_name) LIKE :term
            ORDER BY metabo_name ASC
            LIMIT :per_page
            OFFSET :offset
        """
        results = conn.execute(sql.text(query), {
            'term': f'%{term}%',
            'per_page': per_page,
            'offset': (page - 1) * per_page,
        }).all()
        results = [row._asdict() for row in results]

        count_query = """
            SELECT COUNT(*)
            FROM Metabolites
            WHERE LOWER(metabo_name) LIKE LOWER(:term)
        """
        total_count = conn.execute(sql.text(count_query), {'term': f'%{term}%'}).scalar()
        has_more = (page * per_page < total_count)

        return json.dumps({
            'results': results,
            'pagination': {'more': has_more},
        })

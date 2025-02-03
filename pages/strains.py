import json

from flask import render_template, request
import sqlalchemy as sql

from db import get_connection


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
        query = """
            SELECT
                tax_id AS id,
                tax_names AS text
            FROM Taxa
            WHERE LOWER(tax_names) LIKE :term
            ORDER BY tax_names ASC
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
            FROM Taxa
            WHERE LOWER(tax_names) LIKE LOWER(:term)
        """
        total_count = conn.execute(sql.text(count_query), {'term': f'%{term}%'}).scalar()
        has_more = (page * per_page < total_count)

        return json.dumps({
            'results': results,
            'pagination': {'more': has_more},
        })

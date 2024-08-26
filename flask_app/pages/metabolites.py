import re

from flask import render_template
import sqlalchemy as sql

from flask_app.db import get_connection


def metabolite_show_page(cheb_id):
    with get_connection() as conn:
        query = "SELECT * FROM Metabolites WHERE cheb_id = :cheb_id LIMIT 1"
        metabolite = conn.execute(sql.text(query), { 'cheb_id': cheb_id }).one()._asdict()
        numeric_id = re.sub(r'^CHEBI:', '', cheb_id)

        return render_template(
            "pages/metabolites/show.html",
            metabolite=metabolite,
            cheb_id=cheb_id,
            numeric_id=numeric_id
        )

import json

from flask import (
    g,
    render_template,
    request,
)

from db import get_connection
from models import (
    Taxon,
    Strain,
)


def strain_show_page(id):
    strain = g.db_session.get_one(Strain, id)

    return render_template("pages/strains/show.html", strain=strain)


def taxa_completion_json():
    term     = request.args.get('term', '')
    page     = int(request.args.get('page', '1'))
    per_page = 10

    with get_connection() as conn:
        results, has_more = Taxon.search_by_name(conn, term, page, per_page)

        return json.dumps({
            'results': results,
            'pagination': {'more': has_more},
        })

import json

from flask import (
    g,
    render_template,
    request,
    session,
)
import sqlalchemy as sql


def comparison_show_page():
    return "OK"


def comparison_update_json():
    data = request.json
    data['targets'] = list(set(data['targets']))

    session['compareData'] = data

    return json.dumps({ 'targetCount': len(data['targets']) })

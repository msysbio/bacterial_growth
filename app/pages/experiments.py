import io

import sqlalchemy as sql
from flask import (
    g,
    render_template,
)
from werkzeug.exceptions import Forbidden

from app.model.orm import Experiment


def experiment_show_page(publicId):
    experiment = _fetch_experiment(publicId)

    return render_template("pages/experiments/show.html", experiment=experiment)


def _fetch_experiment(publicId):
    experiment = g.db_session.scalars(
        sql.select(Experiment)
        .where(Experiment.publicId == publicId)
        .limit(1)
    ).one()

    if not experiment.study.visible_to_user(g.current_user):
        raise Forbidden()

    return experiment

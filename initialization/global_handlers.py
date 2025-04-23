from uuid import uuid4

from flask import (
    g,
    session,
    render_template,
)
import sqlalchemy.exc as sql_exceptions

from db import get_connection, get_session


def init_global_handlers(app):
    app.before_request(_make_session_permanent)
    app.before_request(_open_db_connection)
    app.before_request(_fetch_user)

    app.after_request(_close_db_connection)

    app.errorhandler(404)(_not_found)
    app.errorhandler(sql_exceptions.NoResultFound)(_not_found)

    app.errorhandler(403)(_forbidden)
    app.errorhandler(500)(_server_error)

    return app


def _make_session_permanent():
    # By default, expires in 31 days
    session.permanent = True


def _open_db_connection():
    if 'db_conn' not in g:
        g.db_conn    = get_connection()
        g.db_session = get_session(g.db_conn)


def _fetch_user():
    if 'user' not in g:
        if 'user_uuid' in session:
            user_uuid = session['user_uuid']
        else:
            # Create a new user UUID so we can keep track of this browser
            # TODO might be temporary, might be useful to convert anonymous users
            user_uuid = str(uuid4())

        session['user_uuid'] = user_uuid
        g.current_user = User(uuid=user_uuid)


def _close_db_connection(response):
    db_conn = g.pop('db_conn', None)
    if db_conn is not None:
        db_conn.close()

    return response


def _not_found(_error):
    return render_template('errors/404.html'), 404


def _forbidden(_error):
    return render_template('errors/403.html'), 403


def _server_error(_error):
    return render_template('errors/500.html'), 500


# TODO (2025-03-12) Temporary, will eventually be fetched from a database
class User:
    def __init__(self, uuid):
        self.uuid = uuid

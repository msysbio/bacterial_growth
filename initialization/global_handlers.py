from uuid import uuid4

from flask import (
    current_app,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
import sqlalchemy as sql
import sqlalchemy.exc as sql_exceptions
from flask_sqlalchemy.record_queries import get_recorded_queries

from db import get_connection, FLASK_DB
from app.model.orm import User
from app.model.lib.errors import LoginRequired


def init_global_handlers(app):
    app.before_request(_make_session_permanent)
    app.before_request(_open_db_connection)
    app.before_request(_fetch_user)

    app.after_request(_close_db_connection)

    app.errorhandler(404)(_render_not_found)
    app.errorhandler(sql_exceptions.NoResultFound)(_render_not_found)

    app.errorhandler(403)(_render_forbidden)
    app.errorhandler(500)(_render_server_error)

    app.errorhandler(LoginRequired)(_redirect_to_login)

    return app


def _make_session_permanent():
    # By default, expires in 31 days
    session.permanent = True


def _open_db_connection():
    if request.endpoint == 'static':
        return

    if 'db_conn' not in g:
        g.db_conn = get_connection()

    if 'db_session' not in g:
        g.db_session = FLASK_DB.session


def _fetch_user():
    if request.endpoint == 'static':
        return

    if 'user' not in g:
        if 'user_uuid' in session:
            user_uuid = session['user_uuid']
        else:
            # Create a new user UUID so we can keep track of this browser
            user_uuid = str(uuid4())

        session['user_uuid'] = user_uuid

        g.current_user = g.db_session.scalars(
            sql.select(User)
            .where(User.uuid == user_uuid)
            .limit(1)
        ).one_or_none()


def _close_db_connection(response):
    if request.endpoint == 'static':
        return response

    if current_app.config['SQLALCHEMY_RECORD_QUERIES']:
        import sqlparse

        recorded_queries = list(get_recorded_queries())

        for query_info in recorded_queries:
            # print(sqlparse.format(query_info.statement, reindent=True))
            duration_ms = round((query_info.end_time - query_info.start_time) * 1_000, 2)
            current_app.logger.info(f"[SQL {duration_ms}ms] " + query_info.statement)

        current_app.logger.info(f"SQL query count: {len(recorded_queries)}")

    db_conn = g.pop('db_conn', None)
    if db_conn is not None:
        db_conn.close()

    return response


def _render_not_found(_error):
    return render_template('errors/404.html'), 404


def _render_forbidden(_error):
    return render_template('errors/403.html'), 403


def _render_server_error(_error):
    return render_template('errors/500.html'), 500


def _redirect_to_login(_error):
    return redirect(url_for('user_login_page'))

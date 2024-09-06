import time
import datetime
import logging

from flask import g, current_app, request
from sqlalchemy import event as sql_event
from sqlalchemy.engine import Engine


def init_timing(app):
    app.before_request(start_request_timing)
    app.after_request(log_request_timing)

    return app


def start_request_timing():
    g.start_time = time.monotonic_ns()


def log_request_timing(response):
    if not request.full_path.startswith('/static'):
        duration_ns = time.monotonic_ns() - g.start_time
        duration_ms = round(duration_ns / 1_000_000, 2)

        logger = current_app.logger.getChild('timing')
        logger.info(f"[{duration_ms}ms] Full request")

    return response


# Reference:
# https://docs.sqlalchemy.org/en/20/faq/performance.html#how-can-i-profile-a-sqlalchemy-powered-application
#
@sql_event.listens_for(Engine, "before_cursor_execute")
def start_db_timing(conn, cursor, statement, parameters, context, executemany):
    start_time = time.monotonic_ns()
    conn.info.setdefault("start_time", []).append(start_time)

@sql_event.listens_for(Engine, "after_cursor_execute")
def log_db_timing(conn, cursor, statement, parameters, context, executemany):
    duration_ns = time.monotonic_ns() - conn.info["start_time"].pop(-1)
    duration_ms = round(duration_ns / 1_000_000, 2)

    logger = current_app.logger.getChild('timing')
    logger.info(f"[{duration_ms}ms] Query: {statement}")

import os
from pathlib import Path

import sqlalchemy as sql

def up(conn):
    initial_schema_file = Path(os.path.dirname(__file__)) / '000_initial_schema.sql'
    initial_schema = initial_schema_file.read_text()

    for statement in initial_schema.split(';'):
        statement = statement.strip()
        if len(statement) > 0:
            conn.execute(sql.text(statement))

def down(conn):
    pass

if __name__ == "__main__":
    from flask_app.lib.migrations import run
    run(__file__, up, down)

import sqlalchemy as sql


def up(conn):
    query = "RENAME TABLE Study to Studies"
    conn.execute(sql.text(query))

    query = "RENAME TABLE Project to Projects"
    conn.execute(sql.text(query))


def down(conn):
    query = "RENAME TABLE Studies to Study"
    conn.execute(sql.text(query))

    query = "RENAME TABLE Projects to Project"
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)

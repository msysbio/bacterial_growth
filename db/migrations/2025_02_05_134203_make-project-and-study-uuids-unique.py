import sqlalchemy as sql


def up(conn):
    query = "ALTER TABLE Project ADD UNIQUE (projectUniqueID)"
    conn.execute(sql.text(query))

    query = "ALTER TABLE Study ADD UNIQUE (studyUniqueID)"
    conn.execute(sql.text(query))


def down(conn):
    query = "ALTER TABLE Project DROP INDEX projectUniqueID"
    conn.execute(sql.text(query))

    query = "ALTER TABLE Study DROP INDEX studyUniqueID"
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from lib.migrations import run
    run(__file__, up, down)

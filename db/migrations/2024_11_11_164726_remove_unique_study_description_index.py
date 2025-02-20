import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE Study
        DROP INDEX studyDescription;
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE Study
        ADD UNIQUE INDEX (studyDescription(255));
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from lib.migrate import run
    run(__file__, up, down)

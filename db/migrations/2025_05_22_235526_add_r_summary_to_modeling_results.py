import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE ModelingResults
        ADD COLUMN rSummary TEXT DEFAULT NULL
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE ModelingResults
        DROP rSummary
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from lib.migrate import run
    run(__file__, up, down)

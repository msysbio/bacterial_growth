import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE ModelingRequests
        MODIFY error TEXT DEFAULT NULL
        ;
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE ModelingRequests
        MODIFY error VARCHAR(100) DEFAULT NULL
        ;
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from lib.migrate import run
    run(__file__, up, down)

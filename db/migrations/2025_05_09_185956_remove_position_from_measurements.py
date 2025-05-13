import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE Measurements
        DROP position;
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE Measurements
        ADD position varchar(100);
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from lib.migrate import run
    run(__file__, up, down)

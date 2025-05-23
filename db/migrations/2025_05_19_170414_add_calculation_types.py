import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE MeasurementContexts
        ADD calculationType varchar(50) COLLATE utf8mb4_bin DEFAULT NULL;
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE Bioreplicates
        ADD calculationType varchar(50) COLLATE utf8mb4_bin DEFAULT NULL;
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE MeasurementContexts
        DROP calculationType;
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE Bioreplicates
        DROP calculationType;
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from lib.migrate import run
    run(__file__, up, down)

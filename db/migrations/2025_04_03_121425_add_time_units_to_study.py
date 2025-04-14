import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE Study
        ADD COLUMN timeUnits VARCHAR(100) COLLATE utf8mb4_bin
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE Study
        DROP COLUMN timeUnits;
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from lib.migrate import run
    run(__file__, up, down)

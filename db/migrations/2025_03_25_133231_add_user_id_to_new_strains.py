import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE Strains
        ADD COLUMN userUniqueID VARCHAR(100) DEFAULT NULL;
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE Strains
        DROP COLUMN userUniqueID;
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)

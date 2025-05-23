import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE Strains
        ADD COLUMN assemblyGenBankId varchar(50) DEFAULT NULL;
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE Strains
        DROP COLUMN assemblyGenBankId;
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)

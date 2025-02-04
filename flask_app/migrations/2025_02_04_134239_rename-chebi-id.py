import sqlalchemy as sql

def up(conn):
    query = """
        ALTER TABLE Metabolites
        CHANGE cheb_id chebi_id varchar(512)
    """
    params = {}

    conn.execute(sql.text(query), params)


def down(conn):
    query = """
        ALTER TABLE Metabolites
        CHANGE chebi_id cheb_id varchar(512)
    """
    params = {}

    conn.execute(sql.text(query), params)


if __name__ == "__main__":
    from flask_app.lib.migrations import run
    run(__file__, up, down)

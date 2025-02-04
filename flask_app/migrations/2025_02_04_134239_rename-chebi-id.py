import sqlalchemy as sql

def up(conn):
    conn.execute(sql.text("ALTER TABLE Metabolites CHANGE cheb_id chebi_id varchar(512)"))
    conn.execute(sql.text("ALTER TABLE MetabolitePerExperiment CHANGE cheb_id chebi_id varchar(255)"))


def down(conn):
    conn.execute(sql.text("ALTER TABLE Metabolites CHANGE chebi_id cheb_id varchar(512)"))
    conn.execute(sql.text("ALTER TABLE MetabolitePerExperiment CHANGE chebi_id cheb_id varchar(255)"))


if __name__ == "__main__":
    from flask_app.lib.migrations import run
    run(__file__, up, down)

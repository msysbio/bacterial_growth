import sqlalchemy as sql


def up(conn):
    conn.execute(sql.text("ALTER TABLE MetabolitePerExperiment DROP COLUMN experimentId"))
    conn.execute(sql.text("ALTER TABLE MetabolitePerExperiment DROP COLUMN bioreplicateId"))
    conn.execute(sql.text("ALTER TABLE MetabolitePerExperiment DROP COLUMN metabo_name"))


def down(conn):
    conn.execute(sql.text("""
        ALTER TABLE MetabolitePerExperiment
        ADD COLUMN metabo_name varchar(255)
    """))
    conn.execute(sql.text("""
        ALTER TABLE MetabolitePerExperiment
        ADD COLUMN bioreplicateId varchar(100) NOT NULL
    """))
    conn.execute(sql.text("""
        ALTER TABLE MetabolitePerExperiment
        ADD COLUMN experimentId varchar(100) NOT NULL
    """))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)

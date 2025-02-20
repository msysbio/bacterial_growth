import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE MetabolitePerExperiment
        DROP PRIMARY KEY,
        ADD PRIMARY key(experimentUniqueId, bioreplicateUniqueId, cheb_id);
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE Abundances
        DROP PRIMARY KEY,
        ADD PRIMARY key(experimentUniqueId, bioreplicateUniqueId, memberId);
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE MetabolitePerExperiment
        DROP PRIMARY KEY,
        ADD PRIMARY key(experimentId, bioreplicateId, cheb_id);
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE Abundances
        DROP PRIMARY KEY,
        ADD PRIMARY key(experimentId, bioreplicateId, memberId);
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from lib.migrate import run
    run(__file__, up, down)

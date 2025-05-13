import sqlalchemy as sql


def up(conn):
    query = "RENAME TABLE CompartmentsPerExperiment to ExperimentCompartments"
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE ExperimentCompartments
        DROP experimentId,
        DROP compartmentId,
        DROP communityId,
        DROP CONSTRAINT CompartmentsPerExperiment_fk_3,
        DROP communityUniqueId,
        CHANGE experimentUniqueId experimentId INT NOT NULL,
        CHANGE compartmentUniqueId compartmentId INT NOT NULL
        ;
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE ExperimentCompartments
        CHANGE experimentId experimentUniqueId INT NOT NULL,
        CHANGE compartmentId compartmentUniqueId INT NOT NULL,
        ADD experimentId varchar(100) COLLATE utf8mb4_bin NOT NULL,
        ADD compartmentId varchar(100) COLLATE utf8mb4_bin NOT NULL,
        ADD communityId varchar(100) COLLATE utf8mb4_bin NOT NULL,
        ADD communityUniqueId INT DEFAULT NULL
        ;
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE ExperimentCompartments
        ADD CONSTRAINT CompartmentsPerExperiment_fk_3
            FOREIGN KEY (communityUniqueId)
            REFERENCES Communities (id)
            ON DELETE SET NULL ON UPDATE CASCADE
        ;
    """
    conn.execute(sql.text(query))

    query = "RENAME TABLE ExperimentCompartments to CompartmentsPerExperiment"
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from lib.migrate import run
    run(__file__, up, down)

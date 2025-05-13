import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE CompartmentsPerExperiment

        DROP CONSTRAINT CompartmentsPerExperiment_fk_1,
        DROP CONSTRAINT CompartmentsPerExperiment_fk_2,
        DROP CONSTRAINT CompartmentsPerExperiment_fk_3,
        DROP PRIMARY KEY,

        ADD id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,

        DROP experimentId,
        DROP compartmentId,
        DROP communityId
        ;
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE CompartmentsPerExperiment

        ADD experimentId varchar(100) COLLATE utf8mb4_bin NOT NULL,
        ADD compartmentId varchar(100) COLLATE utf8mb4_bin NOT NULL,
        ADD communityId varchar(100) COLLATE utf8mb4_bin NOT NULL,

        ADD CONSTRAINT CompartmentsPerExperiment_fk_1
            FOREIGN KEY (experimentUniqueId)
            REFERENCES Experiments (experimentUniqueId)
            ON DELETE CASCADE ON UPDATE CASCADE,
        ADD CONSTRAINT CompartmentsPerExperiment_fk_2
            FOREIGN KEY (compartmentUniqueId)
            REFERENCES Compartments (compartmentUniqueId)
            ON DELETE CASCADE ON UPDATE CASCADE,
        ADD CONSTRAINT CompartmentsPerExperiment_fk_3
            FOREIGN KEY (communityUniqueId)
            REFERENCES Community (communityUniqueId)
            ON DELETE CASCADE ON UPDATE CASCADE
        ;
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE CompartmentsPerExperiment
        DROP PRIMARY KEY,
        ADD PRIMARY KEY (experimentUniqueId, compartmentUniqueId, communityUniqueId),
        DROP COLUMN id
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from lib.migrate import run
    run(__file__, up, down)

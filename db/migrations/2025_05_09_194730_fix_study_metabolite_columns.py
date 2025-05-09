import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE MetabolitePerExperiment

        DROP CONSTRAINT MetabolitePerExperiment_fk_2,
        DROP PRIMARY KEY,
        ADD id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,

        DROP experimentUniqueId,
        DROP bioreplicateUniqueId
        ;
    """
    conn.execute(sql.text(query))

    query = "RENAME TABLE MetabolitePerExperiment to StudyMetabolites"
    conn.execute(sql.text(query))


def down(conn):
    query = "RENAME TABLE StudyMetabolites to MetabolitePerExperiment"
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE MetabolitePerExperiment
        ADD experimentUniqueId int,
        ADD bioreplicateUniqueId int,
        DROP PRIMARY KEY,
        ADD PRIMARY KEY (experimentUniqueId, bioreplicateUniqueId, chebi_id),
        ADD CONSTRAINT MetabolitePerExperiment_fk_2
            FOREIGN KEY (experimentUniqueId)
            REFERENCES Experiments (id)
            ON DELETE CASCADE ON UPDATE CASCADE,
        DROP COLUMN id
        ;
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from lib.migrate import run
    run(__file__, up, down)
